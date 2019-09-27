import bothub_backend
import bothub_nlp_api.settings
from functools import wraps
from flask import request


def backend():
    return bothub_backend.get_backend(
        'bothub_backend.bothub.BothubBackend',
        bothub_nlp_api.settings.BOTHUB_ENGINE_URL
    )


NEXT_LANGS = {
    'english': [
        'en',
    ],
    'portuguese': [
        'pt',
        'pt_br',
    ],
    'pt': [
        'pt_br',
    ],
    'pt-br': [
        'pt_br',
    ],
    'br': [
        'pt_br',
    ],
}


class AuthorizationIsRequired(Exception):
    def __init__(self, payload=None):
        Exception.__init__(self)
        self.message = 'Authorization is required'
        self.status_code = 401
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class ValidationError(Exception):
    def __init__(self, message, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = 400
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def get_repository_authorization():
    authorization_header_value = request.headers.get('Authorization')
    authorization_uuid = \
        authorization_header_value and authorization_header_value[7:]

    if not authorization_uuid:
        return False

    return authorization_uuid


def authorization_required(f):
    @wraps(f)
    def check(*args, **kwargs):
        repository_authorization = get_repository_authorization()
        if not repository_authorization:
            raise AuthorizationIsRequired()
        return f(*args, **kwargs)

    check.__doc__ = f.__doc__
    check.__name__ = f.__name__
    return check
