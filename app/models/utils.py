from app.models.base_models import DATABASE

from app.models.models import Bot, Profile


def create_schema():
    DATABASE.connect()
    models = [Bot, Profile]
    DATABASE.create_tables(models)

    print("SCHEMA CREATED.")
