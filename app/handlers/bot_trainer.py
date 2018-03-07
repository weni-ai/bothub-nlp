""" This module will train all bots. """
import logging

from tornado.web import asynchronous
from tornado.gen import coroutine
from app.handlers.base import BothubBaseHandler
from app.utils import authorization_required
from app.core.train import train_update
from app.settings import SUPPORTED_LANGUAGES


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

        for language in SUPPORTED_LANGUAGES:
            current_update = repository.current_update(language)
            train_update(current_update, repository_authorization.user)

        self.write({
            'repository_uuid': repository.uuid.hex,
            'languages': SUPPORTED_LANGUAGES,
        })
