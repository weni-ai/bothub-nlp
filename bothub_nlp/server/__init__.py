import logging

from tornado.web import Application, url

from .. import settings
from .handlers.parse import ParseHandler
from .handlers.train import TrainHandler
from .handlers.info import InfoHandler


logging.basicConfig(format=settings.LOGGER_FORMAT)
logger = logging.getLogger('bothub NLP server')
logger.setLevel(settings.LOGGER_LEVEL)


app = None


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
    import tornado.ioloop

    load_app()

    logger.info('Starting server in {} port'.format(settings.PORT))

    tornado.ioloop.IOLoop.current().start()
