import logging

from typing import Text
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
    evaluate_entities,
)

from rasa_nlu.model import Interpreter
from rasa_nlu.components import ComponentBuilder
from rasa_nlu.training_data import Message
from rasa_nlu.training_data import TrainingData

from .utils import PokeLogging
from .utils import get_rasa_nlu_config_from_update, update_interpreters

logger = logging.getLogger(__name__)


def _log_evaluation_table(report: Text,
                          precision: float,
                          f1: float,
                          accuracy: float
                          ) -> None:  # pragma: no cover
    '''
    Log the sklearn evaluation metrics.
    '''

    logger.info('F1-Score:  {}'.format(f1))
    logger.info('Precision: {}'.format(precision))
    logger.info('Accuracy:  {}'.format(accuracy))
    logger.info('Classification report: \n{}'.format(report))


def _collect_nlu_successes(intent_results):
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


def _collect_nlu_errors(intent_results):
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


# def evaluate_entities(targets,
#                       predictions,
#                       tokens,
#                       extractor):  # pragma: no cover
#     '''
#     Creates summary statistics for entity extractor.
#     Logs precision, recall, and F1 per entity type for extractor.
#     '''
#     aligned_predictions = align_all_entity_predictions(targets, predictions,
#                                                        tokens, extractor)

#     merged_targets = merge_labels(aligned_predictions)
#     merged_targets = substitute_labels(merged_targets, 'O', 'no_entity')

#     result = {}

#     merged_predictions = merge_labels(aligned_predictions, extractor)
#     merged_predictions = substitute_labels(merged_predictions,
#                                            'O',
#                                            'no_entity')

#     logger.info('Evaluation for entity extractor: {} '.format(extractor))
#     report, precision, f1, accuracy = get_evaluation_metrics(
#         merged_targets, merged_predictions)
#     _log_evaluation_table(report, precision, f1, accuracy)

#     result[extractor] = {
#         'report': report,
#         'precision': precision,
#         'f1_score': f1,
#         'accuracy': accuracy
#     }

#     return result


def evaluate_intents(intent_results,
                     confmat_filename,
                     intent_hist_filename):  # pragma: no cover
    '''
    Creates a confusion matrix and summary statistics for intent predictions.
    Log samples which could not be classified correctly and save them to file.
    Creates a confidence histogram which is saved to file and send to AWS S3.
    Wrong and correct prediction confidences will be
    plotted in separate bars of the same histogram plot.
    Only considers those examples with a set intent.
    Others are filtered out. Returns a dictionary of containing the
    evaluation result.
    '''
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
        targets, predictions)
    _log_evaluation_table(report, precision, f1, accuracy)

    print(intent_results)

    successs = _collect_nlu_successes(intent_results)
    errors = _collect_nlu_errors(intent_results)

    print(successs)
    print(errors)

    cnf_matrix = confusion_matrix(targets, predictions)
    labels = unique_labels(targets, predictions)
    plot_confusion_matrix(cnf_matrix, classes=labels,
                          title='Intent Confusion matrix',
                          out=confmat_filename)
    plt.show()

    plot_intent_confidences(intent_results,
                            intent_hist_filename)

    plt.show()

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
        'accuracy': accuracy
    }


def _entity_rasa_nlu_data(entity, evaluate):
    return {
        'start': entity.start,
        'end': entity.end,
        'value': evaluate.text[entity.start:entity.end],
        'entity': entity.entity.value,
    }


# def get_intent_targets(training_examples):  # pragma: no cover
#     return [e.get('intent', '') for e in training_examples]


# def get_entity_targets(training_examples):
#     return [e.get('entities', []) for e in training_examples]


# def get_intent_predictions(targets, interpreter,
#                            test_data):  # pragma: no cover
#     """Runs the model for the test set and extracts intent predictions.
#         Returns intent predictions, the original messages
#         and the confidences of the predictions"""
#     intent_results = []
#     for e, target in zip(test_data, targets):
#         res = interpreter.parse(e.text, only_output_properties=False)
#         intent_results.append(IntentEvaluationResult(
#             target,
#             extract_intent(res),
#             extract_message(res),
#             extract_confidence(res)))

#     return intent_results


def evaluate_update(update, by):
    '''
    :param update: Receives the Repository Update {id}
    :param by: Receives the User {id} that requested the evaluate
    :return:
    '''
    print('RUN EVALUATE')
    # print(dir(update.repository))
    # interpreter = update_interpreters.get(update, use_cache=False)
    print(by)

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

    print(test_data.training_examples)

    for evaluate in training_examples:
        print(evaluate.as_dict())

    rasa_nlu_config = get_rasa_nlu_config_from_update(update)

    # interpreter = Interpreter(rasa_nlu_config.pipeline,
    #                           ComponentBuilder(use_cache=False))

    interpreter = update_interpreters.get(update, use_cache=False)

    print('\n')

    # print(dir(interpreter))
    print('PIPELINE {}'.format(rasa_nlu_config.pipeline))

    extractor = get_entity_extractors(interpreter)
    entity_predictions, tokens = get_entity_predictions(interpreter,
                                                        test_data)

    print(tokens)

    print('EXTRACTOR {}'.format(extractor))

    intent_targets = get_intent_targets(test_data)
    entity_targets = get_entity_targets(test_data)

    print('TRAINING {}'.format(training_examples))
    print('INTENT TARGETS {}'.format(intent_targets))
    print('ENTITY TARGETS {}'.format(entity_targets))

    # intent_results, entity_predictions, tokens = get_predictions(
    #     interpreter, training_examples, intent_targets)

    result = {
        'intent_evaluation': None,
        'entity_evaluation': None
    }

    confmat_filename = 'teste.png'
    intent_hist_filename = 'teste2.png'

    # if is_intent_classifier_present(interpreter):
    #     logger.info('Intent evaluation results:')
    #     result['intent_evaluation'] = evaluate_intents(intent_results,
    #                                                    confmat_filename,
    #                                                    intent_hist_filename)

    # intent_targets = get_intent_targets(test_data)
    intent_results = get_intent_predictions(
        intent_targets, interpreter, test_data)

    print(intent_results)
    print(intent_targets)

    result['intent_evaluation'] = evaluate_intents(intent_results,
                                                   confmat_filename,
                                                   intent_hist_filename)

    if duckling_extractors.intersection(extractor):
        entity_predictions = remove_duckling_entities(entity_predictions)
        extractor = remove_duckling_extractors(extractor)

    result['entity_evaluation'] = evaluate_entities(entity_targets,
                                                    entity_predictions,
                                                    tokens,
                                                    extractor)

    print(result)
    print('END EVALUATE')
    return result
