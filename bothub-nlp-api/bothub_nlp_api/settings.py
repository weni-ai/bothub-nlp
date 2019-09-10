import logging
from collections import OrderedDict
from decouple import config


def cast_supported_languages(i):
    return OrderedDict([
        x.split(':', 1) if ':' in x else (x, x) for x in
        i.split('|')
    ])

BOTHUB_NLP_API_PORT = config(
    'BOTHUB_NLP_API_PORT',
    default=2657,
    cast=int,
)

BOTHUB_NLP_API_LOGGER_FORMAT = config(
    'BOTHUB_NLP_API_LOGGER_FORMAT',
    default='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    cast=str,
)

BOTHUB_NLP_API_LOGGER_LEVEL = config(
    'BOTHUB_NLP_API_LOGGER_LEVEL',
    default=logging.DEBUG,
    cast=int,
)

BOTHUB_NLP_DEBUG = config(
    'BOTHUB_NLP_DEBUG',
    default=False,
    cast=bool,
)

BOTHUB_NLP_DEVELOPMENT_MODE = config(
    'BOTHUB_NLP_DEVELOPMENT_MODE',
    default=BOTHUB_NLP_DEBUG,
    cast=bool,
)

BOTHUB_NLP_SENTRY_CLIENT = config(
    'BOTHUB_NLP_SENTRY_CLIENT',
    default=None,
)

SUPPORTED_LANGUAGES = config(
    'SUPPORTED_LANGUAGES',
    default='en|pt',
    cast=cast_supported_languages,
)

BOTHUB_NLP_CELERY_BROKER_URL = config(
    'BOTHUB_NLP_CELERY_BROKER_URL',
    default='redis://localhost:6379/0',
)

BOTHUB_NLP_CELERY_BACKEND_URL = config(
    'BOTHUB_NLP_CELERY_BACKEND_URL',
    default=BOTHUB_NLP_CELERY_BROKER_URL,
)

BOTHUB_NLP_NLU_AGROUP_LANGUAGE_QUEUE = config(
    'BOTHUB_NLP_NLU_AGROUP_LANGUAGE_QUEUE',
    cast=bool,
    default=True,
)
