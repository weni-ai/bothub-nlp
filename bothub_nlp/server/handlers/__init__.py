import tornado.escape

from tornado.web import RequestHandler
from rest_framework import status
from bothub.common.models import RepositoryAuthorization


class ApiHandler(RequestHandler):
    content_type = 'application/json'

    def set_default_headers(self):
        self.set_header('Content-Type', self.content_type)
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')

    def prepare(self):
        super().prepare()
        self.json_data = None
        request_content_type = self.request.headers.get('Content-Type', None)
        if self.request.method in ['POST'] and \
                self.request.body and \
                request_content_type == 'application/json':
            self.json_data = tornado.escape.json_decode(self.request.body)

    def get_argument(self, arg, default=None):
        if self.json_data:
            return self.json_data.get(arg, default)
        return super().get_argument(arg, default)

    def repository_authorization(self):
        authorization_header_value = self.request.headers.get('Authorization')
        authorization_uuid = authorization_header_value and\
            authorization_header_value[7:]

        if not authorization_uuid:
            return False

        try:
            return RepositoryAuthorization.objects.get(
                uuid=authorization_uuid)
        except RepositoryAuthorization.DoesNotExist:
            return False

    def get(self):
        self.set_status(status.HTTP_405_METHOD_NOT_ALLOWED)
        self.finish()

    def post(self):
        self.set_status(status.HTTP_405_METHOD_NOT_ALLOWED)
        self.finish()

    def options(self):
        self.set_status(status.HTTP_405_METHOD_NOT_ALLOWED)
        self.finish()
