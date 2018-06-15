from tornado.web import asynchronous
from tornado.gen import coroutine

from . import ApiHandler


class ParseHandler(ApiHandler):
    @asynchronous
    @coroutine
    def get(self):
        self.finish('OK')
