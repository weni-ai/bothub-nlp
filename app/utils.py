import uuid

from tornado import web

from app.models.base_models import DATABASE
from app.models.models import Profile

INVALID_TOKEN = 'Invalid token'
DB_FAIL = 'Error or retrieving data from Database'
DUPLICATE_SLUG = 'Slug already exists'
WRONG_TOKEN = 'Auth token is wrong'
MISSING_DATA = 'Missing data'
INVALID_REPOSITORY = 'Bot not found'
ERROR_PATTERN = '{"error": "%s"}'


def token_required(f):
    def check(handler, *args, **kwargs):
        auth_token = handler.request.headers.get('Authorization')
        if auth_token and len(auth_token) == 39 and auth_token.startswith('Bearer '):
            with DATABASE.execution_context():
                owner_profile = Profile.select().where(
                    Profile.uuid == uuid.UUID(auth_token[7:]))

            if len(owner_profile) == 1:
                return f(handler, *args, **kwargs)

            raise web.HTTPError(reason=INVALID_TOKEN, status_code=401)
        else:
            raise web.HTTPError(reason=WRONG_TOKEN, status_code=401)

    check.__doc__ = f.__doc__
    check.__name__ = f.__name__
    return check


def validate_uuid(uuid_string):
    try:
        val = uuid.UUID(uuid_string, version=4)
    except AttributeError:
        return False
    except ValueError:
        return False

    return str(val) == uuid_string
