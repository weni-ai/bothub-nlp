""" This module will manage all predict data. """
import logging
import cloudpickle

from tornado.web import asynchronous, HTTPError
from tornado.gen import coroutine
from rasa_nlu.model import Metadata, Interpreter
from app.handlers.base import BothubBaseHandler, SPACY_LANGUAGES
from app.utils import authorization_required


logger = logging.getLogger('bothub NLP - Message Request Handler')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class MessageRequestHandler(BothubBaseHandler):
    """
    Tornado request handler to predict data.
    """
    @asynchronous
    @coroutine
    @authorization_required
    def post(self):
        msg = self.get_argument('msg', default=None)
        if not msg:
            raise HTTPError(reason='msg is required', status_code=400)

        language = self.get_argument('language', default=None)
        if not language:
            raise HTTPError(reason='language is required', status_code=400)

        repository_authorization = self.repository_authorization()
        repository = repository_authorization.repository

        update = repository.last_trained_update(language)

        if not update:
            raise HTTPError(
                reason='This repository has never been trained',
                status_code=400)

        bot_data = update.get_bot_data()
        bot = cloudpickle.loads(bot_data)
        metadata = Metadata(bot, None)
        interpreter = Interpreter.create(
            metadata,
            {},
            SPACY_LANGUAGES[language])

        self.write({
            'repository_uuid': repository.uuid.hex,
            'update_id': update.id,
            'language': language,
            'msg': msg,
            'answer': interpreter.parse(msg),
        })
