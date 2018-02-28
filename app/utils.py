import uuid

from tornado import web


def authorization_required(f):
    def check(handler, *args, **kwargs):
        repository_authorization = handler.repository_authorization()
        if not repository_authorization:
            raise web.HTTPError(status_code=401)
        return f(handler, *args, **kwargs)

    check.__doc__ = f.__doc__
    check.__name__ = f.__name__
    return check