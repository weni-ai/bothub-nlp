from decouple import config


BOTHUB_NLP_WORKER_ON_DEMAND_PORT = config(
    'BOTHUB_NLP_WORKER_ON_DEMAND_PORT',
    default=2658,
)
