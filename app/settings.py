import redis

from decouple import config


DEBUG = config('DEBUG', default=False, cast=bool)

REDIS_CONNECTION = redis.ConnectionPool(
    host=config('REDIS'),
    port=config('REDIS_PORT'),
    db=config('REDIS_DB'))
