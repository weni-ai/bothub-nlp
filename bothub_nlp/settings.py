import logging

from decouple import config

from bothub.utils import cast_supported_languages


DEBUG = config('DEBUG', default=False, cast=bool)

DEVELOPMENT_MODE = config('DEVELOPMENT_MODE', default=DEBUG, cast=bool)

SUPPORTED_LANGUAGES = config(
    'SUPPORTED_LANGUAGES',
    default='en|pt',
    cast=cast_supported_languages)

PORT = config('PORT', default=2657, cast=int)

LOGGER_FORMAT = config(
    'LOGGER_FORMAT',
    default='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    cast=str)

LOGGER_LEVEL = config(
    'LOGGER_LEVEL',
    default=logging.DEBUG,
    cast=int)

SENTRY_CLIENT = config('NLP_SENTRY_CLIENT', default=None)
