import json
import base64

from rasa_nlu.model import Trainer
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.converters import load_rasa_data
from django.utils import timezone

from app.handlers.base import SPACY_LANGUAGES


def train_update(update, by):
    update.by = by
    update.training_started_at = timezone.now()
    update.save(update_fields=[
        'by',
        'training_started_at',
    ])

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

    update.trained_at = timezone.now()
    update.bot_data = base64.b64encode(bot_data).decode('utf8')
    update.save(update_fields=[
        'trained_at',
        'bot_data',
    ])

    return {
        'data': data,
        'intents': list(set(map(lambda x: x.get('intent'), common_examples))),
    }
