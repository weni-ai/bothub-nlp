from tornado.web import asynchronous
from tornado.gen import coroutine

from . import ApiHandler
from ..utils import ValidationError


class ParseHandler(ApiHandler):
    @asynchronous
    @coroutine
    def get(self):
        self.set_header('Content-Type', 'text/plain')
        self.finish('OK')

    @asynchronous
    @coroutine
    def post(self):
        text = self.get_argument('text', default=None)
        language = self.get_argument('language', default=None)

        if not text:
            raise ValidationError('text field is required', field='text')

        self.finish({'text': text, 'language': language})
