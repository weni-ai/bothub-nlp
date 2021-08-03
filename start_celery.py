import subprocess
from bothub_nlp_celery.actions import queue_name
from bothub_nlp_celery import settings

if settings.BOTHUB_LANGUAGE_MODEL != "None":
    queue_name = queue_name(settings.BOTHUB_NLP_LANGUAGE_QUEUE, model_name=settings.BOTHUB_LANGUAGE_MODEL,)
else:
    queue_name = settings.BOTHUB_NLP_LANGUAGE_QUEUE


subprocess.run(
    [
        "celery",
        "-A",
        "celery_app",
        "worker",
        "--autoscale",
        "1,1",
        "-O",
        "fair",
        #"--workdir",
        #".",
        "-c",
        "5",
        "-l",
        "INFO",
        "-E",
        "--pool",
        "solo",
        "-Q",
        queue_name,
    ]
)
