""" This module will train all bots. """
import logging
import json
import uuid
import tornado.escape

from tornado.web import HTTPError, asynchronous
from tornado.gen import coroutine
from app.handlers.base import BothubBaseHandler
from app.utils import token_required


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
    @token_required
    def post(self):
        raise HTTPError(status_code=401)
