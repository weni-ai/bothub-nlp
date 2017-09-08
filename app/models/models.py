from peewee import *
from base_models import BaseModel
from datetime import datetime

import uuid


class Bot(BaseModel):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4)
    bot = TextField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(Bot, self).save(*args, **kwargs)

    class Meta:
        db_table = 'bots'
