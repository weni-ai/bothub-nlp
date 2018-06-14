import logging

from decouple import config


DEBUG = config('DEBUG', default=False, cast=bool)

SUPPORTED_LANGUAGES = config(
    'SUPPORTED_LANGUAGES',
    cast=lambda v: v.split())

PORT = config('PORT', default=8001, cast=int)

LOGGER_FORMAT = config(
    'LOGGER_FORMAT',
    default='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    cast=str)

LOGGER_LEVEL = config(
    'LOGGER_LEVEL',
    default=logging.DEBUG,
    cast=int)

IMPORT_ALL_LANGUAGES_BEFORE_MAKE_APP = config(
    'IMPORT_ALL_LANGUAGES_BEFORE_MAKE_APP',
    default=False,
    cast=bool)