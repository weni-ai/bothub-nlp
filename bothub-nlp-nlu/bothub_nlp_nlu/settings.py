from decouple import config


BOTHUB_NLP_WORKER_ON_DEMAND_PORT = config(
    'BOTHUB_NLP_WORKER_ON_DEMAND_PORT',
    default=2658,
)
BOTHUB_NLP_DOCKER_CLIENT_BASE_URL = config(
    'BOTHUB_NLP_DOCKER_CLIENT_BASE_URL',
    default='unix://var/run/docker.sock',
)
BOTHUB_NLP_WORKER_DOCKER_IMAGE_NAME = config(
    'BOTHUB_NLP_WORKER_DOCKER_IMAGE_NAME',
    default='ilha/bothub-nlp',
)
BOTHUB_NLP_WORKER_DOWN_TIME = config(
    'BOTHUB_NLP_WORKER_DOWN_TIME',
    cast=int,
    default=10,
)
BOTHUB_NLP_WORKER_NETWORKS = config(
    'BOTHUB_NLP_WORKER_NETWORKS',
    cast=lambda v: [s.strip() for s in v.split(',')],
    default='bothub-nlp')
BOTHUB_NLP_WORKER_BLOCK_ON_SWARM_MANAGER = config(
    'BOTHUB_NLP_WORKER_BLOCK_ON_SWARM_MANAGER',
    cast=bool,
    default=True)
