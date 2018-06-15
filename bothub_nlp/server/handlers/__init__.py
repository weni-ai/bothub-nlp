from tornado.web import RequestHandler
from bothub.common.models import RepositoryAuthorization


class ApiHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')

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

    def options(self):
        self.set_status(204)
        self.finish()

    def options(self):
        self.set_status(204)
        self.finish()
