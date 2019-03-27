from rasa_nlu.evaluate import evaluate_intents, evaluate_entities
from rasa_nlu.evaluate import get_intent_predictions, get_entity_predictions
from rasa_nlu.evaluate import get_entity_extractors
from rasa_nlu.training_data import Message
from django.db import models

from .train import BothubTrainingData
from .utils import get_rasa_nlu_config_from_update
from .utils import update_interpreters
from .utils import PokeLogging
from . import logger

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

            # TODO: This result needs to be handled and stored.
            return result

        except Exception as e:
            logger.exception(e)
            update.test_fail()
            raise e

        finally:
            update.training_log = pl.getvalue()
            update.save(update_fields=['testing_log'])
