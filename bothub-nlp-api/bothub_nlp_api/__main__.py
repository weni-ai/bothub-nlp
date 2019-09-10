import logging

from .app import start
from . import settings


logging.basicConfig(
    format=settings.BOTHUB_NLP_API_LOGGER_FORMAT,
    level=settings.BOTHUB_NLP_API_LOGGER_LEVEL,
)

if settings.BOTHUB_NLP_DEVELOPMENT_MODE:
    import os
    import tornado.autoreload
    tornado.autoreload.start()
    for dir, _, files in os.walk('bothub_nlp'):
        for f in files:
            if not f.startswith('.'):
                tornado.autoreload.watch(
                    '{dir}/{name}'.format(
                        dir=dir,
                        name=f,
                    ),
                )
start()
