import logging
import tornado.ioloop

from tornado.web import Application, url

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
    app.listen(settings.PORT)


def start():
    load_app()

    logger.info('Starting server in {} port'.format(settings.PORT))

    tornado.ioloop.IOLoop.current().start()
