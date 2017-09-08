from base_models import DATABASE, BaseModel

import inspect
import models

DATABASE.connect()
m = [
    models.Bot
]
DATABASE.create_tables(m)
print("SCHEMA CREATED.")
