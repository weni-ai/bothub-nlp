from app.models.base_models import DATABASE

from app.models.models import Repository, Profile, RepositoryAuthorization


def create_schema():
    DATABASE.connect()
    models = [Repository, Profile, RepositoryAuthorization]
    DATABASE.create_tables(models)

    print("SCHEMA CREATED.")
