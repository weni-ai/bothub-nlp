# Bothub NLP API Service

This is a Python Web service.

## Environment Variables

| Variable | Type | Default | Description |
|--|--|--|--|
| ENVIRONMENT | `str` | `production` |  |
| BOTHUB_NLP_API_HOST | `str` | `0.0.0.0` | Web service ip |
| BOTHUB_NLP_API_PORT | `int` | `2657` | Web service port |
| BOTHUB_NLP_SENTRY_CLIENT | `bool` | `None` | Enable Sentry Client |
| BOTHUB_NLP_SENTRY | `str` | `None` | Sentry Client URL |
| SUPPORTED_LANGUAGES | `str` | `en|pt` | Set supported languages. Separe languages using |. You can set location follow the format: [LANGUAGE_CODE]:[LANGUAGE_LOCATION]. |
| BOTHUB_ENGINE_URL | `str` | `https://api.bothub.it` | Web service url |
| BOTHUB_NLP_CELERY_BROKER_URL | `str` | `redis://localhost:6379/0	` | `Celery Broker URL, check usage instructions in Celery Docs` |
| BOTHUB_NLP_CELERY_BACKEND_URL | `str` | `BOTHUB_NLP_CELERY_BROKER_URL` value | Celery Backend URL, check usage instructions in [Celery Docs](http://docs.celeryproject.org/en/latest/index.html) |
| BOTHUB_NLP_NLU_AGROUP_LANGUAGE_QUEUE | `boolean` | `True` | Agroup tasks by language in celery queue, if `True` there will be only one queue per language. |
| BOTHUB_NLP_API_WORKERS_PER_CORE | `int` | `3` |  |
| BOTHUB_NLP_API_WEB_CONCURRENCY | `int` | `None` |  |
| BOTHUB_NLP_API_LOG_LEVEL | `str` | `info` |  |
| BOTHUB_NLP_API_KEEPALIVE | `int` | `120` |  |
