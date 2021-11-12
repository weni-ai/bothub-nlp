import subprocess
from bothub_nlp_celery.actions import queue_name
from bothub_nlp_celery import settings

if settings.BOTHUB_LANGUAGE_MODEL:
    queue = queue_name(settings.BOTHUB_NLP_LANGUAGE_QUEUE, model_name=settings.BOTHUB_LANGUAGE_MODEL,)
else:
    queue = settings.BOTHUB_NLP_LANGUAGE_QUEUE


subprocess.run(
    [
        "celery",
        "-A",
        "celery_app",
        "worker",
        "-O",
        "fair",
        "-c",
        "1",
        "-l",
        "INFO",
        "-E",
        "--pool",
        "gevent",
        "-Q",
        queue,
    ]
)
