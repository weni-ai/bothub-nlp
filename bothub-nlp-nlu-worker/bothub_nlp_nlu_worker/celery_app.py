from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_PARSE_TEXT
from bothub_nlp_celery.tasks import TASK_NLU_TRAIN_UPDATE
from bothub_nlp_celery.tasks import TASK_NLU_EVALUATE_UPDATE
# from bothub_nlp_nlu.parse import parse_text as parse_text_core
from bothub_nlp_nlu.train import train_update as train_update_core
# from bothub_nlp_nlu.evaluate import evaluate_update as evaluate_update_core


# @celery_app.task(name=TASK_NLU_PARSE_TEXT)
# def parse_text(update_id, repository_authorization, *args, **kwargs):
#     return parse_text_core(update_id, repository_authorization, *args, **kwargs)


@celery_app.task(name=TASK_NLU_TRAIN_UPDATE)
def train_update(update_id, by_id, repository_authorization):
    return train_update_core(update_id, by_id, repository_authorization)


# @celery_app.task(name=TASK_NLU_EVALUATE_UPDATE)
# def evaluate_update(update_id, by_id, repository_authorization):
#     return evaluate_update_core(update_id, by_id, repository_authorization)
