import subprocess
from bothub_nlp_celery.actions import queue_name
from bothub_nlp_celery import settings

subprocess.run(
    [
        "celery",
        "worker",
        "--autoscale",
        "50,10",
        "-O",
        "fair",
        "--workdir",
        "bothub_nlp_nlu_worker",
        "-A",
        "celery_app",
        "-c",
        "1",
        "-l",
        "INFO",
        "-E",
        "-Q",
        queue_name(settings.BOTHUB_NLP_LANGUAGE_QUEUE, model_name=settings.BOTHUB_LANGUAGE_MODEL)
    ]
)
