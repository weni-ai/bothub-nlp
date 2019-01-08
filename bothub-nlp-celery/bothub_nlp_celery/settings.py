from decouple import config


BOTHUB_NLP_CELERY_BROKER_URL = config(
    'BOTHUB_NLP_CELERY_BROKER_URL',
    default='redis://localhost:6379/0',
)

BOTHUB_NLP_CELERY_BACKEND_URL = config(
    'BOTHUB_NLP_CELERY_BACKEND_URL',
    default=BOTHUB_NLP_CELERY_BROKER_URL,
)

BOTHUB_NLP_AGROUP_LANGUAGE_QUEUE = config(
    'BOTHUB_NLP_AGROUP_LANGUAGE_QUEUE',
    cast=bool,
    default=True,
)
