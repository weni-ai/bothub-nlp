import subprocess
from bothub_nlp_celery.actions import queue_name
from bothub_nlp_celery import settings

subprocess.run(
    [
        "celery",
        "worker",
        "--autoscale",
        "1,1",
        "-O",
        "fair",
        "--workdir",
        "bothub_nlp_nlu_worker",
        "-A",
        "celery_app",
        "-c",
        "5",
        "-l",
        "INFO",
        "-E",
        "--pool",
        "threads",
        "-Q",
        queue_name(
            settings.BOTHUB_NLP_LANGUAGE_QUEUE,
            model_name=settings.BOTHUB_LANGUAGE_MODEL,
        ),
    ]
)
