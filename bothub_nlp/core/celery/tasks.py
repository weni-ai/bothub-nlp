from . import celery_app
from ..parse import parse_text as parse_text_core
from bothub.common.models import RepositoryUpdate


@celery_app.task
def parse_text(update_id, *args, **kwargs):
    update = RepositoryUpdate.objects.get(id=update_id)
    return parse_text_core(update, *args, **kwargs)
