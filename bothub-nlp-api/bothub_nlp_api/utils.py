import bothub_backend
from tornado.web import HTTPError
from decouple import config


def backend():
    return bothub_backend.get_backend(
        'bothub_backend.bothub.BothubBackend', 
        config('BOTHUB_ENGINE_URL', default='https://api.bothub.it')
    )

NEXT_LANGS = backend().get_langs()


class ApiError(HTTPError):
    def __init__(self, msg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg = msg


class ValidationError(ApiError):
    def __init__(self, *args, field=None, status_code=None, **kwargs):
        super().__init__(
            *args,
            status_code=400,
            **kwargs)
        self.field = field


class AuthorizationIsRequired(ApiError):
    def __init__(self, *args, **kwargs):
        super().__init__(
            'Authorization is required',
            *args,
            status_code=401,
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
