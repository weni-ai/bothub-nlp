import tornado.web
from tornado import gen

from . import ApiHandler
from ..utils import authorization_required


class InfoHandler(ApiHandler):
    @tornado.web.asynchronous
    @gen.engine
    @authorization_required
    def get(self):
        repository_authorization = self.repository_authorization()
        info = self.request_backend_parse('info', repository_authorization)
        self.finish(info)
