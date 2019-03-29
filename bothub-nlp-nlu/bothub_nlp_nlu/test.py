from rasa_nlu.evaluate import *
from rasa_nlu.training_data import Message
from django.db import models

from bothub.common.models import RepositoryValidationResult
from bothub.common.models import Evaluation

from .train import BothubTrainingData
from .utils import get_rasa_nlu_config_from_update
from .utils import update_interpreters
from .utils import PokeLogging
from . import logger


def evaluate_intents(intent_results):

    intent_results = remove_empty_intent_examples(intent_results)

    targets, predictions = _targets_predictions_from(intent_results)

    report, precision, f1, accuracy = get_evaluation_metrics(
        targets, predictions, output_dict=True)

    predictions = [
        {
            "text": res.message,
            "intent": res.target,
            "predicted": res.prediction,
            "confidence": res.confidence
        } for res in intent_results
    ]

    return {
        "predictions": predictions,
        "report": report,
        "precision": precision,
        "f1_score": f1,
        "accuracy": accuracy
    }


def evaluate_entities(targets, predictions, tokens, extractor):

    # ???: This may generate some problems because extractor is not an array
    aligned_predictions = align_all_entity_predictions(targets, predictions,
                                                       tokens, extractor)
    merged_targets = merge_labels(aligned_predictions)
    merged_targets = substitute_labels(merged_targets, "O", "no_entity")

    merged_predictions = merge_labels(aligned_predictions, extractor)
    merged_predictions = substitute_labels(
        merged_predictions, "O", "no_entity")
    logger.info("Evaluation for entity extractor: {} ".format(extractor))

    report, precision, f1, accuracy = get_evaluation_metrics(
        merged_targets, merged_predictions, output_dict=True)

    return {
        "report": report,
        "precision": precision,
        "f1_score": f1,
        "accuracy": accuracy
    }


def test_update(update, by):
    '''

    :param update: Receives the Repository Update {id}
    :param by: Receives the User {id} that requested the training
    :return:
    '''
    update.start_training(by)
    with PokeLogging() as pl:
        try:
            # Get existing validations in the `update` repository.
            validations = [
                Message.build(
                    text=validation.get_text(update.language),
                    intent=validation.intent,
                    entities=[
                        validation_entity.rasa_nlu_data
                        for validation_entity in validation.get_entities(
                            update.language)])
                for validation in update.validations]

            # ???: Not sure what's happening in here
            label_validations_query = update.validations \
                .filter(entities__entity__label__isnull=False) \
                .annotate(entities_count=models.Count('entities')) \
                .filter(entities_count__gt=0)

            # Get existing labels for validation entities
            label_validations = [
                Message.build(
                    text=validation.get_text(update.language),
                    entities=[
                        validation_entity.get_rasa_nlu_data(
                            label_as_entity=True)
                        for validation_entity in filter(
                            lambda ee: ee.entity.label,
                            validation.get_entities(update.language))])
                for validation in label_validations_query]

            # Get the RASA configuration being used for Bothub.
            rasa_nlu_config = get_rasa_nlu_config_from_update(update)

            result = {
                "intent_evaluation": None,
                "entity_evaluation": None
            }

            intent_targets = [validation.get('intent') for validation in validations]
            entity_targets = [validation.get('entities') for validation in validations]

            interpreter = update_interpreters.get(update, use_cache=True)

            test_data = BothubTrainingData(
                label_training_examples=label_validations,
                training_examples=validations)

            intent_results = get_intent_predictions(
                intent_targets, interpreter, test_data)

            extractors = get_entity_extractors(interpreter)
            entity_predictions, tokens = get_entity_predictions(interpreter,
                                                                test_data)

            result['intent_evaluation'] = evaluate_intents(intent_results)

            result['entity_evaluation'] = evaluate_entities(entity_targets,
                                                            entity_predictions,
                                                            tokens,
                                                            extractors)

            from bothub.common.models import IntentReport
            from bothub.common.models import IntentPrediction

            reports = result['intent_evaluation']['report']

            intent_evaluation = Evaluation.objects.create(
                precision=result['intent_evaluation']['precision'],
                f1_score =result['intent_evaluation']['f1_score'],
                accuracy=result['intent_evaluation']['accuracy']
            )

            for intent in reports.keys():
                IntentReport.objects.create(
                    intent=intent,
                    evaluation=intent_evaluation,
                    precision=reports[intent]['precision'],
                    recall=reports[intent]['recall'],
                    f1_score=reports[intent]['f1_score'],
                    support=reports[intent]['support']
                )

            predictions = result['intent_evaluation']['predictions']

            for prediction in predictions:
                IntentPrediction.objects.create(
                    evaluation=intent_evaluation,
                    text=prediction['text'],
                    intent=prediction['intent'],
                    predicted=prediction['predicted'],
                    confidence=prediction['confidence']
                )

            from bothub.common.models import EntityReport

            entity_evaluation = Evaluation.objects.create(
                precision=result['entity_evaluation']['precision'],
                f1_score=result['entity_evaluation']['f1_score'],
                accuracy=result['entity_evaluation']['accuracy']
            )

            reports = result['entity_evaluation']['report']

            for entity in reports.keys():
                EntityReport.objects.create(
                    entity=RepositoryEntity.get(value=entity),
                    evaluation=entity_evaluation,
                    precision=reports[entity]['precision'],
                    recall=reports[entity]['recall'],
                    f1_score=reports[entity]['f1_score'],
                    support=reports[entity]['support']
                )

            RepositoryValidationResult.objects.create(
                intent_evaluation=intent_evaluation,
                entity_evaluation=entity_evaluation
            )

        except Exception as e:
            logger.exception(e)
            update.test_fail()
            raise e

        finally:
            update.training_log = pl.getvalue()
            update.save(update_fields=['testing_log'])
