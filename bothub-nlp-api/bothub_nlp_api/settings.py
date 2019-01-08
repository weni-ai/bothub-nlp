import logging
from decouple import config


BOTHUB_NLP_API_PORT = config(
    'BOTHUB_NLP_API_PORT',
    default=2657,
    cast=int,
)

BOTHUB_NLP_API_LOGGER_FORMAT = config(
    'BOTHUB_NLP_API_LOGGER_FORMAT',
    default='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    cast=str,
)

BOTHUB_NLP_API_LOGGER_LEVEL = config(
    'BOTHUB_NLP_API_LOGGER_LEVEL',
    default=logging.DEBUG,
    cast=int,
)
