import logging
import tornado.ioloop

from tornado.web import Application, url
from tornado.httpserver import HTTPServer
from raven.contrib.tornado import AsyncSentryClient
from bothub.common import languages

from .. import settings
from .handlers.parse import ParseHandler
from .handlers.train import TrainHandler
from .handlers.info import InfoHandler


app = None

logger = logging.getLogger('bothub_nlp.server')

NEXT_LANGS = {
    'english': [
        languages.LANGUAGE_EN,
    ],
    'portuguese': [
        languages.LANGUAGE_PT,
        languages.LANGUAGE_PT_BR,
    ],
    languages.LANGUAGE_PT: [
        languages.LANGUAGE_PT_BR,
    ],
    'pt-br': [
        languages.LANGUAGE_PT_BR,
    ],
    'br': [
        languages.LANGUAGE_PT_BR,
    ],
}


def make_app():
    return Application([
        url('/', ParseHandler),
        url('/parse/', ParseHandler),
        url('/train/', TrainHandler),
        url('/info/', InfoHandler),
    ])


def load_app():
    global app
    app = make_app()

    if settings.SENTRY_CLIENT:
        app.sentry_client = AsyncSentryClient(settings.SENTRY_CLIENT)

    if settings.DEVELOPMENT_MODE:
        app.listen(settings.PORT)
    else:
        server = HTTPServer(app)
        server.listen(settings.PORT)
        server.start(0)


def start():
    load_app()

    logger.info('Starting server in {} port'.format(settings.PORT))

    tornado.ioloop.IOLoop.current().start()
