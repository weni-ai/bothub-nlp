INVALID_TOKEN = "invalid_token"
DB_FAIL = "db_fail"
DUPLICATE_SLUG = "duplicated_slug"


def token_required(f):
    def check(handler, *args, **kwargs):
        auth_token = handler.request.headers.get('Authorization')
        if auth_token and len(auth_token) == 39 and auth_token.startswith('Bearer '):
            return f(handler, *args, **kwargs)
        else:
            handler.set_status(401)
            handler.write("Auth token wrong")
            handler.finish()
    check.__doc__ = f.__doc__
    check.__name__ = f.__name__
    return check
