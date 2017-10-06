from decouple import config

import peewee


DATABASE = peewee.PostgresqlDatabase(
    config('BOTHUB_POSTGRES_DB'),
    user=config('BOTHUB_POSTGRES_USER'),
    password=config('BOTHUB_POSTGRES_PASSWORD'),
    host=config('BOTHUB_POSTGRES'),
    port=config('BOTHUB_POSTGRES_PORT'))


class BaseModel(peewee.Model):
    class Meta:
        database = DATABASE
