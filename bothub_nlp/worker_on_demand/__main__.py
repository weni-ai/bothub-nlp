import logging

from ..core.celery import celery_app
from .. import settings

from . import MyDemand


logging.basicConfig(level=logging.DEBUG)
MyDemand(
    celery_app,
    api_server_address=(
        '0.0.0.0',
        settings.BOTHUB_NLP_WORKER_ON_DEMAND_PORT,
    ),
).run()
