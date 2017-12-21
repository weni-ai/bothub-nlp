from app.models.base_models import BaseModel
from datetime import datetime

import uuid
import peewee
import json


class JSONField(peewee.TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)


class Profile(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = peewee.DateTimeField(default=datetime.now)
    updated_at = peewee.DateTimeField()

    def __str__(self):  # pragma: no cover
        r = {}
        for k in self._data.keys():
            try:
                r[k] = str(getattr(self, k))
            except:
                r[k] = json.dumps(getattr(self, k))
        return str(r)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(Profile, self).save(*args, **kwargs)

    class Meta:
        db_table = 'profiles'


class Repository(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, default=uuid.uuid4)
    bot = peewee.BlobField()
    slug = peewee.CharField(unique=True, null=False)
    intents = JSONField()
    private = peewee.BooleanField(default=False)
    created_at = peewee.DateTimeField(default=datetime.now)
    created_by = peewee.ForeignKeyField(Profile, related_name='repository_created_by')
    updated_at = peewee.DateTimeField()
    updated_by = peewee.ForeignKeyField(Profile, related_name='repository_updated_by')

    def to_dict(self):
        return {
            'uuid': str(self.uuid),
            'slug': self.slug
        }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(Repository, self).save(*args, **kwargs)

    def __str__(self):  # pragma: no cover
        r = {}
        for k in self._data.keys():
            try:
                r[k] = str(getattr(self, k))
            except:
                r[k] = json.dumps(getattr(self, k))
        return str(r)

    class Meta:
        db_table = 'repositories'


class RepositoryAuthorization(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, default=uuid.uuid4)
    profile = peewee.ForeignKeyField(Profile, related_name='profile')
    repository = peewee.ForeignKeyField(Repository)
    permission = peewee.SmallIntegerField()
    created_at = peewee.DateTimeField(default=datetime.now)
    created_by = peewee.ForeignKeyField(Profile, related_name='repository_authorization_created_by')
    updated_at = peewee.DateTimeField()
    updated_by = peewee.ForeignKeyField(Profile, related_name='repository_authorization_updated_by')

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(RepositoryAuthorization, self).save(*args, **kwargs)

    class Meta:
        db_table = 'repositories_authorizations'
