import json

from rasa_nlu.model import Trainer
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.converters import load_rasa_data

from app.handlers.base import SPACY_LANGUAGES


def train_update(update, by):
    update.start_training(by)

    try:
        rasa_nlu_config = {
            'pipeline': 'spacy_sklearn',
            'path': './models',
            'data': './data.json',
            'language': update.language,
        }
        data = {
            'rasa_nlu_data': update.rasa_nlu_data,
        }

        trainer = Trainer(
            RasaNLUConfig(json.dumps(rasa_nlu_config)),
            SPACY_LANGUAGES[update.language])
        trainer.train(load_rasa_data(json.dumps(data)))
        bot_data = trainer.persist()
        common_examples = data.get('rasa_nlu_data').get('common_examples')
    except Exception as e:  # pragma: no cover
        update.train_fail()  # pragma: no cover
        raise e  # pragma: no cover

    update.save_training(bot_data)

    return {
        'data': data,
        'intents': list(set(map(lambda x: x.get('intent'), common_examples))),
    }
