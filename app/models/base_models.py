import peewee
from decouple import config

DATABASE = peewee.PostgresqlDatabase('bothub', user='postgres',
                                     password='postgres', host=config('BOTHUB_POSTGRES'), port=config('BOTHUB_POSTGRES_PORT'))


class BaseModel(peewee.Model):
    class Meta:
        database = DATABASE
