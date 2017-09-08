from base_models import DATABASE

import models


DATABASE.connect()
m = [
    models.Bot
]
DATABASE.create_tables(m)

print("SCHEMA CREATED.")
