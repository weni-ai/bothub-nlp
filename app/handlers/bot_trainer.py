""" This module will train all bots. """
import logging
import json
import uuid
import tornado.escape

from tornado.web import HTTPError, asynchronous
from tornado.gen import coroutine
from rasa_nlu.model import Trainer
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.converters import load_rasa_data
from django.utils import timezone
from app.handlers.base import BothubBaseHandler, SPACY_LANGUAGES
from app.utils import authorization_required


logger = logging.getLogger('bothub NLP - Bot Trainer Request Handler')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class BotTrainerRequestHandler(BothubBaseHandler):
    """
    Tornado request handler to train bot.
    """

    @asynchronous
    @coroutine
    @authorization_required
    def post(self):
        repository_authorization = self.repository_authorization()
        repository = repository_authorization.repository

        language = self.get_argument('language', default=None)
        if not language:
            raise HTTPError(reason='language is required', status_code=400)
        
        current_update = repository.current_update(language)
        current_update.by = repository_authorization.user
        current_update.training_started_at = timezone.now()
        current_update.save(update_fields=[
            'by',
            'training_started_at',
        ])
            
        rasa_nlu_config = {
            'pipeline': 'spacy_sklearn',
            'path' : './models',
            'data' : './data.json',
            'language': language
        }
        data = {
            'rasa_nlu_data': current_update.rasa_nlu_data,
        }
        
        trainer = Trainer(RasaNLUConfig(json.dumps(rasa_nlu_config)), SPACY_LANGUAGES[language])
        trainer.train(load_rasa_data(json.dumps(data)))
        bot_data = trainer.persist()
        common_examples = data.get('rasa_nlu_data').get('common_examples')

        intents = list(set(map(lambda x: x.get('intent'), common_examples)))

        current_update.trained_at = timezone.now()
        current_update.bot_data = bot_data
        current_update.save(update_fields=[
            'trained_at',
            'bot_data',
        ])

        self.write({
            'repository_uuid': repository.uuid.hex,
            'language': language,
            'intents': intents,
            'data': data,
        })
