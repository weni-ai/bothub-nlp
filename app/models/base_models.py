import peewee
from decouple import config

DATABASE = peewee.PostgresqlDatabase('bothub', user='postgres',
                                     password='postgres', host=config('BOTHUB_POSTGRIS'))


class BaseModel(peewee.Model):
    class Meta:
        database = DATABASE
