from tempfile import mkdtemp
from collections import defaultdict

from rasa_nlu.model import Trainer
from rasa_nlu.training_data import Message, TrainingData
from rasa_nlu.components import ComponentBuilder
from rasa_nlu.training_data.formats.readerwriter import TrainingDataWriter
from rasa_nlu.utils import json_to_string
from django.db import models

from .utils import get_rasa_nlu_config_from_update
from .persistor import BothubPersistor


class BothubWriter(TrainingDataWriter):
    def dumps(self, training_data, **kwargs):
        js_entity_synonyms = defaultdict(list)
        for k, v in training_data.entity_synonyms.items():
            if k != v:
                js_entity_synonyms[v].append(k)

        formatted_synonyms = [{'value': value, 'synonyms': syns}
                              for value, syns in js_entity_synonyms.items()]

        formatted_examples = [
            example.as_dict()
            for example in training_data.training_examples
        ]
        formatted_label_examples = [
            example.as_dict()
            for example in training_data.label_training_examples or []
        ]

        return json_to_string({
            'rasa_nlu_data': {
                'common_examples': formatted_examples,
                'label_examples': formatted_label_examples,
                'regex_features': training_data.regex_features,
                'entity_synonyms': formatted_synonyms,
            }
        }, **kwargs)


class BothubTrainingData(TrainingData):
    def __init__(self, label_training_examples=None, **kwargs):
        if label_training_examples:
            self.label_training_examples = self.sanitize_examples(
                label_training_examples)
        else:
            self.label_training_examples = []
        super().__init__(**kwargs)

    def as_json(self, **kwargs):
        return BothubWriter().dumps(self)


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
    path_temp = mkdtemp()
    trainer.persist(
        path_temp,
        persistor=persistor,
        project_name=str(update.repository.uuid),
        fixed_model_name=str(update.id))
