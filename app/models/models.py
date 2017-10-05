from models.base_models import BaseModel
from datetime import datetime

import uuid
import peewee


class Profile(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = peewee.DateTimeField(default=datetime.now)
    updated_at = peewee.DateTimeField()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(Profile, self).save(*args, **kwargs)

    class Meta:
        db_table = 'profiles'


class Bot(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, default=uuid.uuid4)
    bot = peewee.BlobField()
    slug = peewee.CharField(unique=True, null=False)
    owner = peewee.ForeignKeyField(Profile)
    created_at = peewee.DateTimeField(default=datetime.now)
    updated_at = peewee.DateTimeField()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(Bot, self).save(*args, **kwargs)

    class Meta:
        db_table = 'bots'
