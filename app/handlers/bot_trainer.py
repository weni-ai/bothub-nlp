""" This module will train all bots. """
import logging
import json
import tornado.escape

from tornado.web import HTTPError, asynchronous
from tornado.gen import coroutine
from app.rasabot import RasaBotTrainProcess
from app.handlers.base import BothubBaseHandler
from app.models.models import Bot, Profile
from app.models.base_models import DATABASE
from app.settings import DEBUG, REDIS_CONNECTION
from app.utils import token_required, MISSING_DATA


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
    @token_required
    def post(self):
        if self.request.body:
            json_body = tornado.escape.json_decode(self.request.body)
            auth_token = self.request.headers.get('Authorization')[7:]
            language = json_body.get("language", None)
            bot_slug = json_body.get("slug", None)
            data = json.dumps(json_body.get("data", None))
            private = json_body.get("private", False)

            bot = RasaBotTrainProcess(language, data, self.callback, auth_token, bot_slug, private)
            bot.daemon = True
            bot.start()
        else:
            raise HTTPError(reason=MISSING_DATA, status_code=401)

    def callback(self, data):
        if isinstance(data, HTTPError):
            self.set_status(data.status_code, data.reason)
            self.write_error(data.status_code)
            return

        self.write(data)
        self.finish()




