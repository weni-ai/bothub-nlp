import logging
import json
import uuid
import requests

from rasa_nlu.training_data import Message
from rasa_nlu.training_data import TrainingData
from rasa_nlu.evaluate import (
    merge_labels,
    align_all_entity_predictions,
    substitute_labels,
    get_evaluation_metrics,
    is_intent_classifier_present,
    get_entity_targets,
    get_entity_extractors,
    get_intent_targets,
    plot_intent_confidences,
    plot_confusion_matrix,
    get_intent_predictions,
    get_entity_predictions,
    _targets_predictions_from,
)

from .utils import update_interpreters

logger = logging.getLogger(__name__)

excluded_itens = [
    'micro avg',
    'macro avg',
    'weighted avg',
    'no_entity',
    'no predicted',
]


def remove_empty_intent_examples(intent_results):
    filtered = []
    for r in intent_results:
        if r.prediction is None:
            r = r._replace(prediction='no predicted')

        if r.target != '' and r.target is not None:
            filtered.append(r)

    return filtered


def collect_nlu_successes(intent_results):
    successes = [{'text': r.message,
                  'intent': r.target,
                  'intent_prediction': {'name': r.prediction,
                                        'confidence': r.confidence,
                                        },
                  'status': 'success'}
                 for r in intent_results if r.target == r.prediction]
    return successes


def collect_nlu_errors(intent_results):
    errors = [{'text': r.message,
               'intent': r.target,
               'intent_prediction': {'name': r.prediction,
                                     'confidence': r.confidence,
                                     },
               'status': 'error'}
              for r in intent_results if r.target != r.prediction]
    return errors


def evaluate_entities(targets,
                      predictions,
                      tokens,
                      extractors):  # pragma: no cover
    aligned_predictions = align_all_entity_predictions(targets, predictions,
                                                       tokens, extractors)
    merged_targets = merge_labels(aligned_predictions)
    merged_targets = substitute_labels(merged_targets, 'O', 'no_entity')

    for extractor in extractors:
        merged_predictions = merge_labels(aligned_predictions, extractor)
        merged_predictions = substitute_labels(
            merged_predictions, 'O', 'no_entity')
        report, precision, f1, accuracy = get_evaluation_metrics(
            merged_targets, merged_predictions, output_dict=True)

        result = {
            'report': report,
            'precision': precision,
            'f1_score': f1,
            'accuracy': accuracy
        }

    return result


def evaluate_intents(intent_results):  # pragma: no cover
    intent_results = remove_empty_intent_examples(intent_results)
    targets, predictions = _targets_predictions_from(intent_results)

    report, precision, f1, accuracy = get_evaluation_metrics(
        targets, predictions, output_dict=True)

    log = collect_nlu_errors(intent_results) + \
        collect_nlu_successes(intent_results)

    predictions = [
        {
            'text': res.message,
            'intent': res.target,
            'predicted': res.prediction,
            'confidence': res.confidence
        } for res in intent_results
    ]

    return {
        'predictions': predictions,
        'report': report,
        'precision': precision,
        'f1_score': f1,
        'accuracy': accuracy,
        'log': log,
    }


def plot_and_save_charts(update, intent_results):
    import io
    import boto3
    import matplotlib as mpl
    mpl.use('Agg')

    import matplotlib.pyplot as plt
    from sklearn.metrics import confusion_matrix
    from sklearn.utils.multiclass import unique_labels
    from botocore.exceptions import ClientError
    from decouple import config

    aws_access_key_id = config('BOTHUB_NLP_AWS_ACCESS_KEY_ID', default='')
    aws_secret_access_key = config(
        'BOTHUB_NLP_AWS_SECRET_ACCESS_KEY', default='')
    aws_bucket_name = config('BOTHUB_NLP_AWS_S3_BUCKET_NAME', default='')
    aws_region_name = config('BOTHUB_NLP_AWS_REGION_NAME', 'us-east-1')

    confmat_url = ''
    intent_hist_url = ''

    if all([aws_access_key_id, aws_secret_access_key, aws_bucket_name]):
        confmat_filename = 'repository_{}/confmat_{}.png'.format(
            update.id, uuid.uuid4())
        intent_hist_filename = 'repository_{}/intent_hist_{}.png'.format(
            update.id, uuid.uuid4())

        intent_results = remove_empty_intent_examples(intent_results)
        targets, predictions = _targets_predictions_from(intent_results)

        cnf_matrix = confusion_matrix(targets, predictions)
        labels = unique_labels(targets, predictions)
        plot_confusion_matrix(cnf_matrix, classes=labels,
                              title='Intent Confusion matrix')

        chart = io.BytesIO()
        fig = plt.gcf()
        fig.set_size_inches(20, 20)
        fig.savefig(chart, format='png', bbox_inches='tight')
        chart.seek(0)

        s3_client = boto3.client('s3',
                                 aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key,
                                 region_name=aws_region_name,
                                 )
        try:
            s3_client.upload_fileobj(chart, aws_bucket_name, confmat_filename,
                                     ExtraArgs={
                                         'ContentType': 'image/png'})
            confmat_url = '{}/{}/{}'.format(s3_client.meta.endpoint_url,
                                            aws_bucket_name, confmat_filename)
        except ClientError as e:
            logger.error(e)

        plot_intent_confidences(intent_results, None)
        chart = io.BytesIO()
        fig = plt.gcf()
        fig.set_size_inches(10, 10)
        fig.savefig(chart, format='png', bbox_inches='tight')
        chart.seek(0)

        try:
            s3_client.upload_fileobj(chart, aws_bucket_name,
                                     intent_hist_filename,
                                     ExtraArgs={
                                         'ContentType': 'image/png'})
            intent_hist_url = '{}/{}/{}'.format(s3_client.meta.endpoint_url,
                                                aws_bucket_name,
                                                intent_hist_filename)
        except ClientError as e:
            logger.error(e)

    return {
        'matrix_chart': confmat_url,
        'confidence_chart': intent_hist_url,
    }


def entity_rasa_nlu_data(entity, evaluate):
    return {
        'start': entity.start,
        'end': entity.end,
        'value': evaluate.text[entity.start:entity.end],
        'entity': entity.entity.value,
    }

def request_backend_start_evaluation(update_id):
    backend = 'http://33d0c44b.ngrok.io'
    update = requests.get(
        '{}/v2/repository/nlp/authorization/evaluate/evaluations/?update_id={}'.format(
            backend,
            update_id
        )
    ).json()
    return update


def request_backend_create_evaluateresults(
    update_id, 
    matrix_chart, 
    confidence_chart, 
    log,
    intentprecision,
    intentf1_score,
    intentaccuracy,
    entityprecision,
    entityf1_score,
    entityaccuracy):
    backend = 'http://33d0c44b.ngrok.io'
    update = requests.post(
        '{}/v2/repository/nlp/authorization/evaluate/evaluateresults/'.format(
            backend,
        ),
        data={
            'update_id': update_id,
            'matrix_chart': matrix_chart,
            'confidence_chart': confidence_chart,
            'log': log,
            'intentprecision': intentprecision,
            'intentf1_score': intentf1_score,
            'intentaccuracy': intentaccuracy,
            'entityprecision': entityprecision,
            'entityf1_score': entityf1_score,
            'entityaccuracy': entityaccuracy
        }
    ).json()
    return update

def request_backend_create_evaluateresultsintent(
    evaluate_id, 
    precision, 
    recall, 
    f1_score,
    support,
    intent_key):
    backend = 'http://33d0c44b.ngrok.io'
    update = requests.post(
        '{}/v2/repository/nlp/authorization/evaluate/evaluateresultsintent/'.format(
            backend,
        ),
        data={
            'evaluate_id': evaluate_id,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'support': support,
            'intent_key': intent_key
        }
    ).json()
    return update

def request_backend_create_evaluateresultsscore(
    evaluate_id, 
    update_id, 
    precision, 
    recall,
    f1_score,
    support,
    entity_key):
    backend = 'http://33d0c44b.ngrok.io'
    update = requests.post(
        '{}/v2/repository/nlp/authorization/evaluate/evaluateresultsscore/'.format(
            backend,
        ),
        data={
            'evaluate_id': evaluate_id,
            'update_id': update_id,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'support': support,
            'entity_key': entity_key
        }
    ).json()
    return update

def evaluate_update(update, by):
    print(update)
    evaluations = request_backend_start_evaluation(update)
    training_examples = []

    for evaluate in evaluations:
        training_examples.append(
            Message.build(
                text=evaluate.get('text'),
                intent=evaluate.get('intent'),
                entities=evaluate.get('entities')
            )
        )

    test_data = TrainingData(training_examples=training_examples)
    interpreter = update_interpreters.get(update, use_cache=False)
    extractor = get_entity_extractors(interpreter)
    entity_predictions, tokens = get_entity_predictions(interpreter,
                                                        test_data)

    result = {
        'intent_evaluation': None,
        'entity_evaluation': None
    }

    if is_intent_classifier_present(interpreter):
        intent_targets = get_intent_targets(test_data)
        intent_results = get_intent_predictions(
            intent_targets, interpreter, test_data)

        result['intent_evaluation'] = evaluate_intents(intent_results)

    if extractor:
        entity_targets = get_entity_targets(test_data)
        result['entity_evaluation'] = evaluate_entities(entity_targets,
                                                        entity_predictions,
                                                        tokens,
                                                        extractor)

    intent_evaluation = result.get('intent_evaluation')
    entity_evaluation = result.get('entity_evaluation')

    charts = plot_and_save_charts(update, intent_results)

    evaluate_result = request_backend_create_evaluateresults(
        update, 
        charts.get('matrix_chart'),
        charts.get('confidence_chart'),
        intent_evaluation.get('log'),
        intent_evaluation.get('precision'),
        intent_evaluation.get('f1_score'),
        intent_evaluation.get('accuracy'),
        entity_evaluation.get('precision'),
        entity_evaluation.get('f1_score'),
        entity_evaluation.get('accuracy')
    )

    intent_reports = intent_evaluation.get('report')
    entity_reports = entity_evaluation.get('report')

    for intent_key in intent_reports.keys():
        if intent_key and intent_key not in excluded_itens:
            intent = intent_reports.get(intent_key)

            request_backend_create_evaluateresultsintent(
                evaluate_result.get('evaluate_id'),
                intent.get('precision'),
                intent.get('recall'),
                intent.get('f1-score'),
                intent.get('support'),
                intent_key
            )

    for entity_key in entity_reports.keys():
        if entity_key and entity_key not in excluded_itens:
            entity = entity_reports.get(entity_key)

            request_backend_create_evaluateresultsscore(
                evaluate_result.get('evaluate_id'),
                update,
                entity.get('precision'),
                entity.get('recall'),
                entity.get('f1-score'),
                entity.get('support'),
                entity_key
            )

    return {
        'id': evaluate_result.get('evaluate_id'),
        'version': evaluate_result.get('evaluate_version'),
    }
