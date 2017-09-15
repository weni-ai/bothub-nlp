import peewee
from decouple import config

DATABASE = peewee.PostgresqlDatabase('bothub', user=config('BOTHUB_POSTGRES_USER'),
                                     password=config('BOTHUB_POSTGRES_PASSWORD'), host=config('BOTHUB_POSTGRES'), port=config('BOTHUB_POSTGRES_PORT'))


class BaseModel(peewee.Model):
    class Meta:
        database = DATABASE
