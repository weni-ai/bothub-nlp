INVALID_TOKEN = "invalid_token"
DB_FAIL = "db_fail"


def token_required(f):
    def check(handler, *args, **kwargs):
        auth_token = handler.request.headers.get('Authorization')
        if auth_token and len(auth_token) == 32:
            return f(handler, *args, **kwargs)
        else:
            handler.set_status(401)
            handler.write("Auth token wrong")
            handler.finish()
    check.__doc__ = f.__doc__
    check.__name__ = f.__name__
    return check
