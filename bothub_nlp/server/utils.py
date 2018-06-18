from tornado import web

class ApiError(web.HTTPError):
    def __init__(self, msg, *args, status=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg = msg
        self.status = status


class ValidationError(ApiError):
    def __init__(self, *args, field=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.field = field
