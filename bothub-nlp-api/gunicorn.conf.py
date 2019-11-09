import json
import multiprocessing

from bothub_nlp_api import settings


default_web_concurrency = settings.BOTHUB_NLP_API_WORKERS_PER_CORE * multiprocessing.cpu_count()
if settings.BOTHUB_NLP_API_WEB_CONCURRENCY:
    web_concurrency = int(settings.BOTHUB_NLP_API_WEB_CONCURRENCY)
    assert web_concurrency > 0
else:
    web_concurrency = max(int(default_web_concurrency), 2)

# Gunicorn config variables
loglevel = settings.BOTHUB_NLP_API_LOG_LEVEL
workers = web_concurrency
bind = f"{settings.BOTHUB_NLP_API_HOST}:{settings.BOTHUB_NLP_API_PORT}"
keepalive = settings.BOTHUB_NLP_API_KEEPALIVE
errorlog = "-"

# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "bind": bind,
    "keepalive": keepalive,
    # Additional, non-gunicorn variables
    "workers_per_core": settings.BOTHUB_NLP_API_WORKERS_PER_CORE,
    "host": settings.BOTHUB_NLP_API_HOST,
    "port": settings.BOTHUB_NLP_API_PORT,
}
print(json.dumps(log_data))
