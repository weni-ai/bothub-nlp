from decouple import config
from collections import OrderedDict


def cast_supported_languages(i):
    return OrderedDict([
        x.split(':', 1) if ':' in x else (x, x) for x in
        i.split('|')
    ])


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
