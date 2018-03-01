""" This module will manage all predict data. """
import logging
import redis
import cloudpickle

from tornado.web import asynchronous, HTTPError
from tornado.gen import coroutine
from app.handlers.base import BothubBaseHandler
from app.settings import REDIS_CONNECTION
from app.utils import authorization_required


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
    def _set_bot_on_redis(self, bot_uuid, bot):
        redis.Redis(connection_pool=REDIS_CONNECTION).set(bot_uuid, bot)

    @asynchronous
    @coroutine
    @authorization_required
    def post(self):
        msg = self.get_argument('msg', default=None)
        if not msg:
            raise HTTPError(reason='msg is required', status_code=400)
        
        self.write({
            'msg': msg,
        })