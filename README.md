# Bothub NLP - Natural Language Processing services

![version 2.2.0](https://img.shields.io/badge/version-2.2.0-blue.svg) [![python 3.6](https://img.shields.io/badge/python-3.6-green.svg)](https://docs.python.org/3.6/whatsnew/changelog.html) [![license AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-red.svg)](https://github.com/udomobi/bothub-nlp/blob/master/LICENSE)

Check the [main Bothub project repository](https://github.com/Ilhasoft/bothub).


## Services

### bothub-nlp-api

### bothub-nlp-nlu-worker

### bothub-nlp-nlu-worker-on-demand

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
| SUPPORTED_LANGUAGES | ```string```| ```en\|pt``` | Set supported languages. Separe languages using ```\|```. You can set location follow the format: ```[LANGUAGE_CODE]:[LANGUAGE_LOCATION]```.
| BOTHUB_NLP_SENTRY_CLIENT | ```bool``` | ```None``` | Sentry Client |
| BOTHUB_NLP_CELERY_BROKER_URL | ```string``` | ```redis://localhost:6379/0	``` | Celery Broker URL, check usage instructions in Celery Docs |
| BOTHUB_NLP_CELERY_BACKEND_URL | ```string``` | ```BOTHUB_NLP_CELERY_BROKER_URL``` value | Celery Backend URL, check usage instructions in Celery Docs
| BOTHUB_NLP_NLU_AGROUP_LANGUAGE_QUEUE | ```boolean``` | ```True``` | Agroup tasks by language in celery queue, if `True` there will be only one queue per language. |
| BOTHUB_NLP_DOCKER_CLIENT_BASE_URL | `string` | `unix://var/run/docker.sock` | Docker Client Rest API URL. |
| BOTHUB_NLP_NLU_WORKER_ON_DEMAND_API_PORT | `int` | `2658` | Port to server API webservice. |
| BOTHUB_NLP_NLU_WORKER_DOCKER_IMAGE_NAME | `string` | `ilha/bothub-nlp-nlu-worker` | Bothub NLP NLU Worker Docker image. |
| BOTHUB_NLP_NLU_WORKER_ON_DEMAND_DOWN_TIME | `int` | `10` | Down worker after x minutes without interaction. |
| BOTHUB_NLP_NLU_WORKER_ON_DEMAND_NETWORKS | List separated by common. | `bothub-nlp` | Networks to assign in new worker service. |
| BOTHUB_NLP_NLU_WORKER_ON_DEMAND_RUN_IN_WORKER_NODE | `boolean` | `False` | Run service just in Workers Nodes in Docker Swarm cluster. |
| BOTHUB_NLP_NLU_WORKER_ON_DEMAND_CONFIG_FILE | `string` | `bothub-nlp-nlu-worker-on-demand.cfg` | |
| BOTHUB_NLP_NLU_WORKER_ON_DEMAND_API_BASIC_AUTHORIZATION | `string` | `None` | Fill `api_basic_authorization` kwarg in [CeleryWorkerOnDemand](https://github.com/Ilhasoft/celery-worker-on-demand#class-celeryworkerondemand) constructor |
| BOTHUB_NLP_AWS_S3_BUCKET_NAME | `str` |  |  |
| BOTHUB_NLP_AWS_ACCESS_KEY_ID | `str` |  |  |
| BOTHUB_NLP_AWS_SECRET_ACCESS_KEY | `str` |  |  |
| BOTHUB_NLP_AWS_REGION_NAME | `str` |  |  |
| BOTHUB_ENGINE_URL | ```string```|  ```https://api.bothub.it``` | Bothub-engine API URL


## Docker Arguments

You need to set --build-arg when you are building docker-compose

| Argument | Type | Default | Description |
|--|--|--|--|
| DOWNLOAD_SPACY_MODELS | ```string```|  ```en:en_core_web_md``` | Set supported languages. Separe languages using ```\|```. You can set location follow the format: ```[LANGUAGE_CODE]:[LANGUAGE_LOCATION]```.
