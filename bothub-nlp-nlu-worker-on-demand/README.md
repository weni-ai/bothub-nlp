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
