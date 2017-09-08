import peewee

DATABASE = peewee.PostgresqlDatabase('bothub', user='postgres', password='postgres', host='localhost')

class BaseModel(peewee.Model):
    class Meta:
        database = DATABASE