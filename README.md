# Bothub NLP - Natural Language Processing services

[![Build Status](https://travis-ci.org/bothub-it/bothub-nlp.svg?branch=master)](https://travis-ci.org/bothub-it/bothub-nlp) [![Coverage Status](https://coveralls.io/repos/github/bothub-it/bothub-nlp/badge.svg?branch=master)](https://coveralls.io/github/bothub-it/bothub-nlp?branch=master) ![version 3.0.1](https://img.shields.io/badge/version-3.0.1-blue.svg) [![python 3.6](https://img.shields.io/badge/python-3.6-green.svg)](https://docs.python.org/3.6/whatsnew/changelog.html) [![license AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-red.svg)](https://github.com/bothub-it/bothub-nlp/blob/master/LICENSE)

Check the [main Bothub project repository](https://github.com/Ilhasoft/bothub).


## Services

### bothub-nlp-nlu-worker

### bothub-nlp-ai-platform

## Packages

### bothub-nlp (python 3.6)

### bothub-nlp-celery (python 3.6)

### bothub-nlp-nlu (python 3.6)


# Requirements

* Python (3.6)
* Docker
* Docker-Compose

## Development

Use ```make``` commands to ```lint```, ```init_env```, ```start_development```.

| Command | Description |
|--|--|
| make lint | Show lint warnings and errors
| make init_env | Init file .env with variables environment
| make start_development | Create .env with variable environment and start build docker


## Environment Variables

You can set environment variables in your OS, write on ```.env``` file or pass via Docker config.

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

## Docker Arguments

You need to set --build-arg when you are building docker-compose

| Argument | Type | Default | Description |
|--|--|--|--|
| DOWNLOAD_MODELS | ```string```|  ```en-BERT``` | Set supported languages. Separe languages using ```\|```. You can set location follow the format: ```[LANGUAGE_CODE]-[LANGUAGE_MODEL]```.
