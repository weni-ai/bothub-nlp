from tornado.web import asynchronous
from tornado.gen import coroutine

from bothub.api.v1.serializers.repository import RepositorySerializer

from . import ApiHandler
from ..utils import authorization_required


class InfoHandler(ApiHandler):
    @asynchronous
    @coroutine
    @authorization_required
    def get(self):
        repository_authorization = self.repository_authorization()
        repository = repository_authorization.repository
        serializer = RepositorySerializer(repository)
        self.finish(serializer.data)
