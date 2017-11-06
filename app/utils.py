from app.models.base_models import DATABASE
from app.models.models import Profile

import uuid


INVALID_TOKEN = 'invalid_token'
DB_FAIL = 'db_fail'
DUPLICATE_SLUG = 'duplicated_slug'
WRONG_TOKEN = 'auth_token_wrong'
MISSING_DATA = 'missing_data'
MSG_INFORMATION = '{"info": "%s"}'


def token_required(f):
    def check(handler, *args, **kwargs):
        auth_token = handler.request.headers.get('Authorization')
        if auth_token and len(auth_token) == 39 and auth_token.startswith('Bearer '):
            with DATABASE.execution_context():
                owner_profile = Profile.select().where(
                    Profile.uuid == uuid.UUID(auth_token[7:]))

            if len(owner_profile) == 1:
                return f(handler, *args, **kwargs)

            handler.set_status(401)
            handler.write(MSG_INFORMATION % INVALID_TOKEN)
            handler.finish()
        else:
            handler.set_status(401)
            handler.write(MSG_INFORMATION % WRONG_TOKEN)
            handler.finish()
    check.__doc__ = f.__doc__
    check.__name__ = f.__name__
    return check
