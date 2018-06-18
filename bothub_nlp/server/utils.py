from tornado.web import HTTPError
from rest_framework import status


class ApiError(HTTPError):
    def __init__(self, msg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg = msg


class ValidationError(ApiError):
    def __init__(self, *args, field=None, status_code=None, **kwargs):
        super().__init__(
            *args,
            status_code=status.HTTP_400_BAD_REQUEST,
            **kwargs)
        self.field = field
