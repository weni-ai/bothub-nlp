import tornado.web
import requests
from tornado import gen

from bothub.api.v1.serializers.repository import RepositorySerializer

from . import ApiHandler
from ..utils import authorization_required


class InfoHandler(ApiHandler):
    @tornado.web.asynchronous
    @gen.engine
    @authorization_required
    def get(self):
        repository_authorization = self.repository_authorization_new_backend()
        info = requests.get(
            'http://7cfc350e.ngrok.io/v2/repository/nlp/authorization/info/{}/'.format(
                repository_authorization
            )
        ).json()
        self.finish(info)
