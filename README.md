# Bothub NLP - Natural Language Processing services

[![Build Status](https://travis-ci.org/bothub-it/bothub-nlp.svg?branch=master)](https://travis-ci.org/bothub-it/bothub-nlp) [![Coverage Status](https://coveralls.io/repos/github/bothub-it/bothub-nlp/badge.svg?branch=master)](https://coveralls.io/github/bothub-it/bothub-nlp?branch=master) ![version 3.0.1](https://img.shields.io/badge/version-3.0.1-blue.svg) [![python 3.6](https://img.shields.io/badge/python-3.6-green.svg)](https://docs.python.org/3.6/whatsnew/changelog.html) [![license AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-red.svg)](https://github.com/bothub-it/bothub-nlp/blob/master/LICENSE)



## Services

### bothub-nlp-nlu-worker

### [bothub-nlp-api](https://github.com/bothub-it/bothub-nlp-api)

## Packages

### [bothub-backend](https://github.com/bothub-it/bothub-backend) (python 3.6)

### [bothub-nlp-celery](https://github.com/bothub-it/bothub-nlp-celery) (python 3.6)


# Requirements

* Python (3.6)
* Docker
* Docker-Compose

## Development

Use ```make``` commands to ```lint```, ```init_env```, ```start_development```.

| Command | Description |
|--|--|
| make init_development_env | Init file .env with variables environment |
| make start_development | Start build docker |
| make install_development_requirements | Install some default models |
| make start_celery | Run celery application |


## Environment Variables

You can set environment variables in your OS, write on ```.env``` file or pass via Docker config.

### bothub-backend

| Variable | Type | Default | Description |
|--|--|--|--|
| BOTHUB_ENGINE_URL | `str` | `https://api.bothub.it` | Web service url |

### nlp-nlu-worker / nlp-ai-platform

You can set environment variables in your OS, write on ```.env``` file or pass via Docker config.

| Variable | Type | Default | Description |
|--|--|--|--|
| WORKER_CACHE_CLEANING_PERIOD | `float` | `3*3600` | Period of time (seconds) the worker will look for idle interpreters to clean cache |
| INTERPRETER_CACHE_IDLE_LIMIT | `float` | `24*3600` | Idle limit of time (seconds) the interpreter cache will keep cache |
| BOTHUB_NLP_AWS_ACCESS_KEY_ID | `str` | | AWS bucket access to save trained models and evaluation results |
| BOTHUB_NLP_AWS_SECRET_ACCESS_KEY | `str` | | AWS bucket access to save trained models and evaluation results |
| BOTHUB_NLP_AWS_S3_BUCKET_NAME | `str` | | AWS bucket access to save trained models and evaluation results |
| BOTHUB_NLP_AWS_REGION_NAME | `str` | | AWS bucket access to save trained models and evaluation results |

### bothub-celery

| Variable | Type | Default | Description |
|--|--|--|--|
| BOTHUB_NLP_CELERY_BROKER_URL | `string` | `redis://localhost:6379/0` | Celery Broker URL, check usage instructions in [Celery Docs](http://docs.celeryproject.org/en/latest/index.html) |
| BOTHUB_NLP_CELERY_BACKEND_URL | `string` | `BOTHUB_NLP_CELERY_BROKER_URL` value | Celery Backend URL, check usage instructions in [Celery Docs](http://docs.celeryproject.org/en/latest/index.html) |
| BOTHUB_NLP_CELERY_SENTRY_CLIENT | `bool` | `False` | Enable Sentry |
| BOTHUB_NLP_CELERY_SENTRY | `str` | `None` | Set URL Sentry Server |
| BOTHUB_NLP_LANGUAGE_QUEUE | `string` | `en` | Set language of model that will be loaded in celery and will define its queue |
| BOTHUB_LANGUAGE_MODEL | `string` | `None` | Set type of model (BERT/SPACY/NONE) |
| TASK_GENERAL_TIME_LIMIT | `int` | `120` | Time limit of celery tasks |
| TASK_PARSE_TIME_LIMIT | `int` | `10` | Time limit of parse task |

## Docker Arguments

You need to set --build-arg when you are building docker-compose

| Argument | Type | Default | Description |
|--|--|--|--|
| DOWNLOAD_MODELS | ```string```|  ```en-BERT``` | Set language and model in build time. Following the format: ```[LANGUAGE_CODE]-[LANGUAGE_MODEL]```.
