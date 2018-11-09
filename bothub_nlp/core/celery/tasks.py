from bothub.common.models import RepositoryUpdate
from bothub.authentication.models import User
from .app import celery_app
from ..parse import parse_text as parse_text_core
from ..train import train_update as train_update_core


@celery_app.task
def parse_text(update_id, *args, **kwargs):
    update = RepositoryUpdate.objects.get(id=update_id)
    return parse_text_core(update, *args, **kwargs)


@celery_app.task
def train_update(update_id, by_id):
    update = RepositoryUpdate.objects.get(id=update_id)
    by = User.objects.get(id=by_id)
    return train_update_core(update, by)
