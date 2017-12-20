""" This module will manage all predict data. """
import logging
import redis
import cloudpickle

from tornado.web import asynchronous
from tornado.gen import coroutine
from app.handlers.base import BothubBaseHandler, SPACY_LANGUAGES
from app.models.base_models import DATABASE
from app.models.models import Bot
from app.settings import DEBUG, REDIS_CONNECTION
from app.utils import token_required
from rasa_nlu.model import Metadata, Interpreter


logger = logging.getLogger('bothub NLP - Message Request Handler')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class MessageRequestHandler(BothubBaseHandler):
    """
    Tornado request handler to predict data.
    """
    @asynchronous
    @coroutine
    @token_required
    def get(self):
        auth_token = self.request.headers.get('Authorization')[7:]
        bot_uuid = self.get_argument('bot', None)
        message = self.get_argument('msg', None)
        redis_bot = redis.Redis(connection_pool=REDIS_CONNECTION).get(bot_uuid)
        if redis_bot is not None:  # pragma: no cover
            if DEBUG:
                logger.info('Reusing from redis...')
            redis_bot = cloudpickle.loads(redis_bot)
            bot_language = 'en'
            metadata = Metadata(redis_bot, None)
            interpreter = Interpreter.load(metadata, {}, SPACY_LANGUAGES[bot_language])
            self.write({
                'bot': dict(uuid=bot_uuid),
                'answer': interpreter.parse(message)
            })
        else:
            if DEBUG:
                logger.info('Creating a new instance...')

            with DATABASE.execution_context():
                try:
                    instance = Bot.get(Bot.uuid == bot_uuid)

                    bot = cloudpickle.loads(instance.bot)
                    bot_language = 'en'
                    metadata = Metadata(bot, None)
                    interpreter = Interpreter.load(metadata, {}, SPACY_LANGUAGES[bot_language])
                    self.write({
                        'bot': dict(uuid=bot_uuid),
                        'answer': interpreter.parse(message)
                    })
                except:
                    pass
