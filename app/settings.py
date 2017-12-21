from decouple import config

import redis
import logging


DEBUG = config('BOTHUB_DEBUG', default=False, cast=bool)

REDIS_CONNECTION = redis.ConnectionPool(host=config('BOTHUB_REDIS'), port=config('BOTHUB_REDIS_PORT'), db=config('BOTHUB_REDIS_DB'))

READ = 0
EDIT = 1
OWNER = 2

ALL_PERMISSIONS = [READ, EDIT, OWNER]

REPOSITORY_PERMISSIONS = [
    'Read',
    'Edit',
    'Owner'
]
