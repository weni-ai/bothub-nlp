import logging

from tornado.web import Application, url

from .. import settings
from .handlers.parse import ParseHandler


logging.basicConfig(format=settings.LOGGER_FORMAT)
logger = logging.getLogger('bothub NLP server')
logger.setLevel(settings.LOGGER_LEVEL)


def make_app():
    return Application([
        url('/', ParseHandler),
        url('/parse/', ParseHandler),
    ])
