import logging
import json

from rasa_nlu.evaluate import (
    merge_labels,
    align_all_entity_predictions,
    substitute_labels,
    get_evaluation_metrics,
    remove_empty_intent_examples,
    is_intent_classifier_present,
    # get_predictions,
    get_entity_targets,
    get_entity_extractors,
    get_intent_targets,

    plot_intent_confidences,
    plot_confusion_matrix,

    _targets_predictions_from,

    extract_entities,
    IntentEvaluationResult,
    extract_intent,
    extract_message,
    extract_confidence,
    get_intent_predictions,
    get_entity_predictions,
    duckling_extractors,
    remove_duckling_entities,
    remove_duckling_extractors,
    # evaluate_entities,
    log_evaluation_table,
)

from rasa_nlu.training_data import Message
from rasa_nlu.training_data import TrainingData

from .utils import update_interpreters

logger = logging.getLogger(__name__)

excluded_itens = ['micro avg', 'macro avg', 'weighted avg', 'no_entity']


def collect_nlu_successes(intent_results):
    '''
    Log messages which result in successful predictions
    and save them to file
    '''
    successes = [{'text': r.message,
                  'intent': r.target,
                  'intent_prediction': {'name': r.prediction,
                                        'confidence': r.confidence,
                                        'status': 'success'}}
                 for r in intent_results if r.target == r.prediction]
    return successes


def collect_nlu_errors(intent_results):
    '''
    Log messages which result in wrong predictions and save them to file
    '''
    errors = [{'text': r.message,
               'intent': r.target,
               'intent_prediction': {'name': r.prediction,
                                     'confidence': r.confidence,
                                     'status': 'error'}}
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
        logger.info('Evaluation for entity extractor: {} '.format(extractor))
        report, precision, f1, accuracy = get_evaluation_metrics(
            merged_targets, merged_predictions, output_dict=True)

        result = {
            'report': report,
            'precision': precision,
            'f1_score': f1,
            'accuracy': accuracy
        }

    return result


def evaluate_intents(intent_results,
                     confmat_filename,
                     intent_hist_filename):  # pragma: no cover
    from sklearn.metrics import confusion_matrix
    from sklearn.utils.multiclass import unique_labels
    import matplotlib.pyplot as plt

    num_examples = len(intent_results)
    intent_results = remove_empty_intent_examples(intent_results)

    logger.info('Intent Evaluation: Only considering those '
                '{} examples that have a defined intent out '
                'of {} examples'.format(len(intent_results), num_examples))

    targets, predictions = _targets_predictions_from(intent_results)

    report, precision, f1, accuracy = get_evaluation_metrics(
        targets, predictions, output_dict=True)
    # log_evaluation_table(report, precision, f1, accuracy)

    log = collect_nlu_errors(intent_results) + \
        collect_nlu_successes(intent_results)

    # cnf_matrix = confusion_matrix(targets, predictions)
    # labels = unique_labels(targets, predictions)
    # plot_confusion_matrix(cnf_matrix, classes=labels,
    #                       title='Intent Confusion matrix',
    #                       out=confmat_filename)
    # plt.show()

    # plot_intent_confidences(intent_results,
    #                         intent_hist_filename)

    # plt.show()

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


def _entity_rasa_nlu_data(entity, evaluate):
    return {
        'start': entity.start,
        'end': entity.end,
        'value': evaluate.text[entity.start:entity.end],
        'entity': entity.entity.value,
    }


def evaluate_update(update, by):
    evaluations = update.repository.evaluations(
        exclude_deleted=False).filter(
            repository_update__language=update.language)

    training_examples = [
        Message.build(
            text=evaluate.get_text(update.language),
            intent=evaluate.intent,
            entities=[
                _entity_rasa_nlu_data(evaluate_entity, evaluate)
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

    confmat_filename = 'teste.png'
    intent_hist_filename = 'teste2.png'

    if is_intent_classifier_present(interpreter):
        intent_targets = get_intent_targets(test_data)
        intent_results = get_intent_predictions(
            intent_targets, interpreter, test_data)

        logger.info("Intent evaluation results:")
        result['intent_evaluation'] = evaluate_intents(intent_results,
                                                       confmat_filename,
                                                       intent_hist_filename)

    if extractor:
        entity_targets = get_entity_targets(test_data)

        logger.info("Entity evaluation results:")
        result['entity_evaluation'] = evaluate_entities(entity_targets,
                                                        entity_predictions,
                                                        tokens,
                                                        extractor)

    # Save a new evaluate report
    from bothub.common.models import RepositoryEntity
    from bothub.common.models import RepositoryEvaluateResult
    from bothub.common.models import RepositoryEvaluateResultScore
    from bothub.common.models import RepositoryEvaluateResultEntity
    from bothub.common.models import RepositoryEvaluateResultIntent

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

    evaluate_result = RepositoryEvaluateResult.objects.create(
        repository_update=update,
        entity_results=entities_score,
        intent_results=intents_score,
        log=json.dumps(intent_evaluation.get('log')),
    )

    intent_reports = intent_evaluation.get('report')
    entity_reports = entity_evaluation.get('report')

    for intent_key in intent_reports.keys():
        if intent_key not in excluded_itens:
            intent = intent_reports.get(intent_key)
            intent_score = RepositoryEvaluateResultScore.objects.create(
                precision=intent.get('precision'),
                recall=intent.get('recall'),
                f1_score=intent.get('f1_score'),
                support=intent.get('support'),
            )

            RepositoryEvaluateResultIntent.objects.create(
                intent=intent_key,
                evaluate_result=evaluate_result,
                score=intent_score,
            )

    for entity_key in entity_reports.keys():
        if entity_key not in excluded_itens:
            entity = entity_reports.get(entity_key)
            entity_score = RepositoryEvaluateResultScore.objects.create(
                precision=entity.get('precision'),
                recall=entity.get('recall'),
                f1_score=entity.get('f1_score'),
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

    print('END EVALUATE')
    return result
