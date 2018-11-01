from celery import Celery
from ... import settings

celery_app = Celery(
    'bothub.core.celery.tasks',
    backend=settings.CELERY_BACKEND_URL,
    broker=settings.CELERY_BROKER_URL)
