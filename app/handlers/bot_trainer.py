""" This module will train all bots. """
import logging

from tornado.web import HTTPError, asynchronous
from tornado.gen import coroutine
from app.handlers.base import BothubBaseHandler
from app.utils import authorization_required
from app.core.train import train_update


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
        train = train_update(current_update, repository_authorization.user)

        self.write({
            'repository_uuid': repository.uuid.hex,
            'language': language,
            'intents': train.get('intents'),
            'data': train.get('data'),
        })
