# Bothub NLP NLU Worker

This the NLU Celery Worker service.

## Environment Variables

| Variable | Type | Default | Description |
|--|--|--|--|
| SUPPORTED_LANGUAGES | `str` | `en|pt` | Set supported languages. Separe languages using |. You can set location follow the format: [LANGUAGE_CODE]:[LANGUAGE_LOCATION]. |
| BOTHUB_ENGINE_URL | `str` | `https://api.bothub.it` | Web service url |
| BOTHUB_NLP_CELERY_BROKER_URL | `str` | `redis://localhost:6379/0	` | `Celery Broker URL, check usage instructions in Celery Docs` |
| BOTHUB_NLP_CELERY_BACKEND_URL | `str` | `BOTHUB_NLP_CELERY_BROKER_URL` value | Celery Backend URL, check usage instructions in [Celery Docs](http://docs.celeryproject.org/en/latest/index.html) |
| BOTHUB_NLP_NLU_AGROUP_LANGUAGE_QUEUE | `boolean` | `True` | Agroup tasks by language in celery queue, if `True` there will be only one queue per language. |
| BOTHUB_NLP_AWS_ACCESS_KEY_ID | `str` |  |  |
| BOTHUB_NLP_AWS_SECRET_ACCESS_KEY | `str` |  |  |
| BOTHUB_NLP_AWS_S3_BUCKET_NAME | `str` |  |  |
| BOTHUB_NLP_AWS_REGION_NAME | `str` |  |  |
| BOTHUB_NLP_LANGUAGE_QUEUE | `str` | en | Set language that will be loaded in celery |
| BOTHUB_NLP_SERVICE_WORKER | `boolean` | `False` | Set true if you are running celery bothub-nlp-nlu-worker |
| BOTHUB_NLP_CELERY_SENTRY_CLIENT | `bool` | `False` |  |
| BOTHUB_NLP_CELERY_SENTRY | `str` | `None` |  |