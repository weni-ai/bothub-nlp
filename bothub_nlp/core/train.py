from tempfile import mkdtemp

from rasa_nlu.model import Trainer
from rasa_nlu.training_data import Message, TrainingData
from rasa_nlu.components import ComponentBuilder

from .utils import get_rasa_nlu_config_from_update
from .persistor import BothubPersistor


def train_update(update, by):
    update.start_training(by)

    examples = [
        Message.build(
            example.get_text(update.language),
            example.intent,
            [
                entity.rasa_nlu_data
                for entity in example.get_entities(update.language)])
        for example in update.examples]

    rasa_nlu_config = get_rasa_nlu_config_from_update(update)
    trainer = Trainer(
        rasa_nlu_config,
        ComponentBuilder(use_cache=False))
    training_data = TrainingData(training_examples=examples)
    trainer.train(training_data)
    persistor = BothubPersistor(update)
    trainer.persist(
        mkdtemp(),
        persistor=persistor,
        project_name=str(update.repository.uuid),
        fixed_model_name=str(update.id))
