from decouple import config
from bothub.utils import cast_supported_languages


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
