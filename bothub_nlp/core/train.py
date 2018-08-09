from tempfile import mkdtemp

from rasa_nlu.model import Trainer
from rasa_nlu.training_data import Message, TrainingData
from rasa_nlu.components import ComponentBuilder
from django.db import models

from .utils import get_rasa_nlu_config_from_update
from .persistor import BothubPersistor


def BothubTrainingData(object):
    def __init__(self, label_training_examples=None, **kwargs):
        if label_training_examples:
            self.label_training_examples = self.sanitize_examples(
                label_training_examples)
        else:
            self.label_training_examples = []
        # super().__init__(**kwargs)


def train_update(update, by):
    update.start_training(by)

    examples = [
        Message.build(
            text=example.get_text(update.language),
            intent=example.intent,
            entities=[
                entity.rasa_nlu_data
                for entity in example.get_entities(update.language)])
        for example in update.examples]

    label_examples_query = update.examples \
        .filter(entities__entity__label__isnull=False) \
        .annotate(entities_count=models.Count('entities')) \
        .filter(entities_count__gt=0)

    label_examples = [
        Message.build(
            text=example.get_text(update.language),
            entities=[
                entity.get_rasa_nlu_data(label_as_entity=True)
                for entity in example.get_entities(update.language)])
        for example in label_examples_query]

    rasa_nlu_config = get_rasa_nlu_config_from_update(update)
    trainer = Trainer(
        rasa_nlu_config,
        ComponentBuilder(use_cache=False))
    training_data = BothubTrainingData(
        label_training_examples=label_examples,
        training_examples=examples)
    trainer.train(training_data)
    persistor = BothubPersistor(update)
    trainer.persist(
        mkdtemp(),
        persistor=persistor,
        project_name=str(update.repository.uuid),
        fixed_model_name=str(update.id))
