import redis

from decouple import config


DEBUG = config('DEBUG', default=False, cast=bool)

SUPPORTED_LANGUAGES = config(
    'SUPPORTED_LANGUAGES',
    cast=lambda v: [s.strip() for s in v.split()])

REDIS_CONNECTION = redis.ConnectionPool(
    host=config('REDIS'),
    port=config('REDIS_PORT'),
    db=config('REDIS_DB'))
