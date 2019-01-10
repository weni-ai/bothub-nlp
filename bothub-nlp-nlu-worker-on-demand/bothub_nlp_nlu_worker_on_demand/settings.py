from decouple import config

BOTHUB_NLP_WORKER_ON_DEMAND_API_PORT = config(
    'BOTHUB_NLP_WORKER_ON_DEMAND_API_PORT',
    default=2658,
    cast=int,
)

BOTHUB_NLP_DOCKER_CLIENT_BASE_URL = config(
    'BOTHUB_NLP_DOCKER_CLIENT_BASE_URL',
    default='unix://var/run/docker.sock',
)
