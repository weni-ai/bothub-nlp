from app.models.base_models import DATABASE

from app.models.models import Bot, Profile


DATABASE.connect()
m = [
    Bot,
    Profile
]
DATABASE.create_tables(m)

print("SCHEMA CREATED.")
