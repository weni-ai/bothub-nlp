""" This module will manage all predict data. """
import logging
import redis
import cloudpickle

from tornado.web import asynchronous
from tornado.gen import coroutine
from app.handlers.base import SPACY_LANGUAGES
from app.handlers.repository_manager import RepositoryManagerHandler
from app.models.base_models import DATABASE
from app.models.models import Repository
from app.settings import DEBUG, REDIS_CONNECTION, ALL_PERMISSIONS
from app.utils import token_required
from rasa_nlu.model import Metadata, Interpreter


logger = logging.getLogger('bothub NLP - Message Request Handler')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class MessageRequestHandler(RepositoryManagerHandler):
    """
    Tornado request handler to predict data.
    """
    allowed_permissions = ALL_PERMISSIONS

    def _set_bot_on_redis(self, bot_uuid, bot):
        redis.Redis(connection_pool=REDIS_CONNECTION).set(bot_uuid, bot)

    @asynchronous
    @coroutine
    @token_required
    def get(self):
        bot_uuid = self.get_argument('bot', None)
        message = self.get_argument('msg', None)
        self._check_repo_user_authorization(bot_uuid)

        redis_bot = redis.Redis(connection_pool=REDIS_CONNECTION).get(bot_uuid)
        if redis_bot is not None:  # pragma: no cover
            if DEBUG:
                logger.info('Reusing from redis...')

            redis_bot = cloudpickle.loads(redis_bot)
            bot_language = 'en'
            metadata = Metadata(redis_bot, None)
            interpreter = Interpreter.create(metadata, {}, SPACY_LANGUAGES[bot_language])
            self.write({
                'bot': dict(uuid=bot_uuid),
                'answer': interpreter.parse(message)
            })
        else:
            if DEBUG:
                logger.info('Using a instance from postgres...')

            with DATABASE.execution_context():
                instance = Repository.select().where(Repository.uuid == bot_uuid).get()
                bot = cloudpickle.loads(instance.bot)

            self._set_bot_on_redis(bot_uuid, cloudpickle.dumps(bot))

            bot_language = 'en'
            metadata = Metadata(bot, None)
            interpreter = Interpreter.create(metadata, {}, SPACY_LANGUAGES[bot_language])
            self.write({
                'bot': dict(uuid=bot_uuid),
                'answer': interpreter.parse(message)
            })
