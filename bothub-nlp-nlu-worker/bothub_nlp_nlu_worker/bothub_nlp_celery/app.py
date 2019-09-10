from celery import Celery
from kombu import Queue

from .actions import ACTION_PARSE
from .actions import ACTION_TRAIN
from .actions import ACTION_EVALUATE
from .actions import queue_name
from . import settings


celery_app = Celery(
    'bothub_nlp_celery',
    broker=settings.BOTHUB_NLP_CELERY_BROKER_URL,
    backend=settings.BOTHUB_NLP_CELERY_BACKEND_URL)

queues_name = set([
    queue_name(ACTION_PARSE, lang)
    for lang in settings.SUPPORTED_LANGUAGES.keys()
] + [
    queue_name(ACTION_TRAIN, lang)
    for lang in settings.SUPPORTED_LANGUAGES.keys()
] + [
    queue_name(ACTION_EVALUATE, lang)
    for lang in settings.SUPPORTED_LANGUAGES.keys()
])
celery_app.conf.task_queues = [
    Queue(queue)
    for queue in queues_name
]
