import peewee
from decouple import config

DATABASE = peewee.PostgresqlDatabase('bothub', user='postgres',
                                     password='postgres', host=config('BOTHUB_POSTGRES'))


class BaseModel(peewee.Model):
    class Meta:
        database = DATABASE
