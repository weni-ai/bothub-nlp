# Bothub NLP NLU Worker On Demand

This service listen Celery Queues to up and down NLU workers on demand.

## Environment Variables

| Variable | Type | Default | Description |
|--|--|--|--|
| BOTHUB_NLP_DOCKER_CLIENT_BASE_URL | `string` | `unix://var/run/docker.sock` | Docker Client Rest API URL. |
| BOTHUB_NLP_NLU_WORKER_ON_DEMAND_API_PORT | `int` | `2658` | Port to server API webservice. |
| BOTHUB_NLP_NLU_WORKER_DOCKER_IMAGE_NAME | `string` | `ilha/bothub-nlp-nlu-worker` | Bothub NLP NLU Worker Docker image. |
| BOTHUB_NLP_NLU_WORKER_ON_DEMAND_DOWN_TIME | `int` | `10` | Down worker after x minutes without interaction. |
| BOTHUB_NLP_NLU_WORKER_ON_DEMAND_NETWORKS | List separated by common. | `bothub-nlp` | Networks to assign in new worker service. |
| BOTHUB_NLP_NLU_WORKER_ON_DEMAND_RUN_IN_WORKER_NODE | `boolean` | `False` | Run service just in Workers Nodes in Docker Swarm cluster. |
| BOTHUB_NLP_NLU_WORKER_ON_DEMAND_CONFIG_FILE | `string` | `bothub-nlp-nlu-worker-on-demand.cfg` | |
| BOTHUB_NLP_NLU_WORKER_ON_DEMAND_API_BASIC_AUTHORIZATION | `string` | `None` | Fill `api_basic_authorization` kwarg in [CeleryWorkerOnDemand](https://github.com/Ilhasoft/celery-worker-on-demand#class-celeryworkerondemand) constructor |
| SUPPORTED_LANGUAGES | `str` | `en|pt` | Set supported languages. Separe languages using |. You can set location follow the format: [LANGUAGE_CODE]:[LANGUAGE_LOCATION]. |
| BOTHUB_ENGINE_URL | `str` | `https://api.bothub.it` | Web service url |
| BOTHUB_NLP_CELERY_BROKER_URL | `str` | `redis://localhost:6379/0	` | `Celery Broker URL, check usage instructions in Celery Docs` |
| BOTHUB_NLP_CELERY_BACKEND_URL | `str` | `BOTHUB_NLP_CELERY_BROKER_URL` value | Celery Backend URL, check usage instructions in [Celery Docs](http://docs.celeryproject.org/en/latest/index.html) |
| BOTHUB_NLP_NLU_AGROUP_LANGUAGE_QUEUE | `boolean` | `True` | Agroup tasks by language in celery queue, if `True` there will be only one queue per language. |
| BOTHUB_NLP_AWS_S3_BUCKET_NAME | `str` |  |  |
| BOTHUB_NLP_AWS_ACCESS_KEY_ID | `str` |  |  |
| BOTHUB_NLP_AWS_SECRET_ACCESS_KEY | `str` |  |  |
| BOTHUB_NLP_AWS_REGION_NAME | `str` |  |  |