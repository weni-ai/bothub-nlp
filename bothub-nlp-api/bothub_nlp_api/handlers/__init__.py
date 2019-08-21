import tornado.escape
import traceback
import requests

from tornado.web import RequestHandler
from rest_framework import status
from raven.contrib.tornado import SentryMixin

from bothub_nlp import settings as bothub_nlp_settings
from ..utils import ApiError, ValidationError


class ApiHandler(SentryMixin, RequestHandler):
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

    def write_error(self, status_code, exc_info):
        r = {}
        if exc_info:
            error_class, error, traceback_instance = exc_info

            if bothub_nlp_settings.BOTHUB_NLP_DEBUG:
                r['traceback'] = traceback.format_exception(
                    error_class, error, traceback_instance)

            if isinstance(error, ValidationError):
                r[error.field] = error.msg
            elif isinstance(error, ApiError):
                r['details'] = error.msg
            else:
                from .. import logger
                logger.error(' '.join(traceback.format_exception(
                    error_class, error, traceback_instance)))

        self.finish(r)

    def repository_authorization(self):
        authorization_header_value = self.request.headers.get('Authorization')
        authorization_uuid = authorization_header_value and\
            authorization_header_value[7:]

        if not authorization_uuid:
            return False

        return authorization_uuid

    def request_backend_parse(self, router, repository_authorization, language=None):
        backend = 'http://ab24300f.ngrok.io'
        update = requests.get(
            '{}/v2/repository/nlp/authorization/{}/{}/?language={}'.format(
                backend,
                router,
                repository_authorization,
                language
            )
        ).json()
        return update

    def get(self):
        self.set_status(status.HTTP_405_METHOD_NOT_ALLOWED)
        self.finish()

    def post(self):
        self.set_status(status.HTTP_405_METHOD_NOT_ALLOWED)
        self.finish()

    def options(self):
        self.set_status(status.HTTP_405_METHOD_NOT_ALLOWED)
        self.finish()
