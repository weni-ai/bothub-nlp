import tornado.web
from tornado import gen
from decouple import config

from . import ApiHandler
from ..utils import authorization_required
from ..utils import backend


class InfoHandler(ApiHandler):
    @tornado.web.asynchronous
    @gen.engine
    @authorization_required
    def get(self):
        repository_authorization = self.repository_authorization()
        info = backend().request_backend_parse('info', repository_authorization)
        self.finish(info)
