from decouple import config
from playhouse.shortcuts import RetryOperationalError

import peewee


class PgDbRetry(RetryOperationalError, peewee.PostgresqlDatabase):
    pass


DATABASE = PgDbRetry(
    config('BOTHUB_POSTGRES_DB'),
    user=config('BOTHUB_POSTGRES_USER'),
    password=config('BOTHUB_POSTGRES_PASSWORD'),
    host=config('BOTHUB_POSTGRES'),
    port=config('BOTHUB_POSTGRES_PORT'))


class BaseModel(peewee.Model):
    class Meta:
        database = DATABASE
