# Bothub NLP Celery Manager

This package abstracts and centralize all Bothub NLP Celery app features.

Usually this package is used as dependencie in a annother packages.

## Environment Variables

| Variable | Type | Default | Description |
|--|--|--|--|
| BOTHUB_NLP_CELERY_BROKER_URL | `string` | `redis://localhost:6379/0` | Celery Broker URL, check usage instructions in [Celery Docs](http://docs.celeryproject.org/en/latest/index.html) |
| BOTHUB_NLP_CELERY_BACKEND_URL | `string` | `BOTHUB_NLP_CELERY_BROKER_URL` value | Celery Backend URL, check usage instructions in [Celery Docs](http://docs.celeryproject.org/en/latest/index.html) |
| BOTHUB_NLP_NLU_AGROUP_LANGUAGE_QUEUE | `boolean` | `True` | Agroup tasks by language in celery queue, if `True` there will be only one queue per language. |
