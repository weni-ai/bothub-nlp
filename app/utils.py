import uuid

from tornado import web


def token_required(f):
    def check(handler, *args, **kwargs):
        raise web.HTTPError(status_code=401)

    check.__doc__ = f.__doc__
    check.__name__ = f.__name__
    return check