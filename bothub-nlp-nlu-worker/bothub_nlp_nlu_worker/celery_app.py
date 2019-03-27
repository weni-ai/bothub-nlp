from bothub.common.models import RepositoryUpdate
from bothub.authentication.models import User
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_PARSE_TEXT, \
    TASK_NLU_TRAIN_UPDATE, TASK_NLU_TEST_UPDATE
from bothub_nlp_nlu.parse import parse_text as parse_text_core
from bothub_nlp_nlu.train import train_update as train_update_core
from bothub_nlp_nlu.test import test_update as test_update_core


@celery_app.task(name=TASK_NLU_PARSE_TEXT)
def parse_text(update_id, *args, **kwargs):
    update = RepositoryUpdate.objects.get(id=update_id)
    return parse_text_core(update, *args, **kwargs)


@celery_app.task(name=TASK_NLU_TRAIN_UPDATE)
def train_update(update_id, by_id):
    update = RepositoryUpdate.objects.get(id=update_id)
    by = User.objects.get(id=by_id)
    return train_update_core(update, by)

@celery_app.task(name=TASK_NLU_TEST_UPDATE)
def test_update(update_id, by_id):
    update = RepositoryUpdate.objects.get(id=update_id)
    by = User.objects.get(id=by_id)
    return test_update_core(update, by)
