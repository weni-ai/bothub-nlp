from tornado.web import HTTPError
from rest_framework import status
from bothub.common import languages


NEXT_LANGS = {
    'english': [
        languages.LANGUAGE_EN,
    ],
    'portuguese': [
        languages.LANGUAGE_PT,
        languages.LANGUAGE_PT_BR,
    ],
    languages.LANGUAGE_PT: [
        languages.LANGUAGE_PT_BR,
    ],
    'pt-br': [
        languages.LANGUAGE_PT_BR,
    ],
    'br': [
        languages.LANGUAGE_PT_BR,
    ],
}


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


class AuthorizationIsRequired(ApiError):
    def __init__(self, *args, **kwargs):
        super().__init__(
            'Authorization is required',
            *args,
            status_code=status.HTTP_401_UNAUTHORIZED,
            **kwargs)


def authorization_required(f):
    def check(handler, *args, **kwargs):
        repository_authorization = handler.repository_authorization()
        if not repository_authorization:
            raise AuthorizationIsRequired()
        return f(handler, *args, **kwargs)

    check.__doc__ = f.__doc__
    check.__name__ = f.__name__
    return check
