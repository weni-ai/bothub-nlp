import logging

from tornado.web import Application, url

from .. import settings
from ..utils import SpacyLanguages
from .handlers.parse import ParseHandler


logging.basicConfig(format=settings.LOGGER_FORMAT)
logger = logging.getLogger('bothub NLP server')
logger.setLevel(settings.LOGGER_LEVEL)

spacyLanguages = SpacyLanguages()


def make_app():
    if settings.IMPORT_ALL_LANGUAGES_BEFORE_MAKE_APP:
        global spacyLanguages
        logger.debug('Importing spacy languages: {}'.format(
            ', '.join(settings.SUPPORTED_LANGUAGES),
        ))
        for language in settings.SUPPORTED_LANGUAGES:
            spacyLanguages[language]
            logger.debug('{} imported'.format(language))
        logger.info('Spacy languages imported!')

    return Application([
        url('/', ParseHandler),
        url('/parse/', ParseHandler),
    ])
