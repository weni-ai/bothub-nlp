import logging
import tornado.ioloop
import multiprocessing

from tornado.web import Application, url
from tornado.httpserver import HTTPServer
from raven.contrib.tornado import AsyncSentryClient
from bothub_nlp import settings as bothub_nlp_settings

from . import settings
from .handlers.parse import ParseHandler
from .handlers.train import TrainHandler
from .handlers.info import InfoHandler
from .handlers.evaluate import EvaluateHandler


app = None

logger = logging.getLogger('bothub_nlp.server')


def make_app():
    return Application([
        url('/', ParseHandler),
        url(r'/parse/?', ParseHandler),
        url(r'/train/?', TrainHandler),
        url(r'/info/?', InfoHandler),
        url(r'/evaluate/?', EvaluateHandler)
    ])


def load_app():
    global app
    app = make_app()

    if bothub_nlp_settings.BOTHUB_NLP_SENTRY_CLIENT:
        app.sentry_client = AsyncSentryClient(
            bothub_nlp_settings.BOTHUB_NLP_SENTRY_CLIENT,
        )

    if bothub_nlp_settings.BOTHUB_NLP_DEVELOPMENT_MODE:
        app.listen(settings.BOTHUB_NLP_API_PORT)
    else:
        server = HTTPServer(app)
        server.listen(settings.BOTHUB_NLP_API_PORT)
        cpu_count = multiprocessing.cpu_count()
        server.start(cpu_count * 2 if cpu_count > 4 else 8)


def start():
    load_app()

    logger.info('Starting server in {} port'.format(
        settings.BOTHUB_NLP_API_PORT,
    ))

    tornado.ioloop.IOLoop.current().start()
