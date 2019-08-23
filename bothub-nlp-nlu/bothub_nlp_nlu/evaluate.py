import logging
import json
import uuid

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

from bothub.common.models import RepositoryEntity
from bothub.common.models import RepositoryEvaluateResult
from bothub.common.models import RepositoryEvaluateResultScore
from bothub.common.models import RepositoryEvaluateResultEntity
from bothub.common.models import RepositoryEvaluateResultIntent

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


def evaluate_update(update, by):
    # evaluations_request = request_backend_start_training(update, by)
    evaluations = update.repository.evaluations(language=update.language)

    training_examples = [
        Message.build(
            text=evaluate.get_text(update.language),
            intent=evaluate.intent,
            entities=[
                entity_rasa_nlu_data(evaluate_entity, evaluate)
                for evaluate_entity in evaluate.get_entities(
                    update.language)])
        for evaluate in evaluations
    ]

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

    intents_score = RepositoryEvaluateResultScore.objects.create(
        precision=intent_evaluation.get('precision'),
        f1_score=intent_evaluation.get('f1_score'),
        accuracy=intent_evaluation.get('accuracy'),
    )

    entities_score = RepositoryEvaluateResultScore.objects.create(
        precision=entity_evaluation.get('precision'),
        f1_score=entity_evaluation.get('f1_score'),
        accuracy=entity_evaluation.get('accuracy'),
    )

    charts = plot_and_save_charts(update, intent_results)
    evaluate_result = RepositoryEvaluateResult.objects.create(
        repository_update=update,
        entity_results=entities_score,
        intent_results=intents_score,
        matrix_chart=charts.get('matrix_chart'),
        confidence_chart=charts.get('confidence_chart'),
        log=json.dumps(intent_evaluation.get('log')),
    )

    intent_reports = intent_evaluation.get('report')
    entity_reports = entity_evaluation.get('report')

    for intent_key in intent_reports.keys():
        if intent_key and intent_key not in excluded_itens:
            intent = intent_reports.get(intent_key)
            intent_score = RepositoryEvaluateResultScore.objects.create(
                precision=intent.get('precision'),
                recall=intent.get('recall'),
                f1_score=intent.get('f1-score'),
                support=intent.get('support'),
            )

            RepositoryEvaluateResultIntent.objects.create(
                intent=intent_key,
                evaluate_result=evaluate_result,
                score=intent_score,
            )

    for entity_key in entity_reports.keys():
        if entity_key and entity_key not in excluded_itens:
            entity = entity_reports.get(entity_key)
            entity_score = RepositoryEvaluateResultScore.objects.create(
                precision=entity.get('precision'),
                recall=entity.get('recall'),
                f1_score=entity.get('f1-score'),
                support=entity.get('support'),
            )

            RepositoryEvaluateResultEntity.objects.create(
                entity=RepositoryEntity.objects.get(
                    repository=update.repository,
                    value=entity_key,
                    create_entity=False),
                evaluate_result=evaluate_result,
                score=entity_score,
            )

    return {
        'id': evaluate_result.id,
        'version': evaluate_result.version,
    }
