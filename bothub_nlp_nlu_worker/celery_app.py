from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_PARSE_TEXT
from bothub_nlp_celery.tasks import TASK_NLU_DEBUG_PARSE_TEXT
from bothub_nlp_celery.tasks import TASK_NLU_SENTENCE_SUGGESTION_TEXT
from bothub_nlp_celery.tasks import TASK_NLU_TRAIN_UPDATE
from bothub_nlp_celery.tasks import TASK_NLU_EVALUATE_UPDATE
from bothub_nlp_celery.tasks import TASK_NLU_WORDS_DISTRIBUTION
from bothub_nlp_nlu.parse import parse_text as parse_text_core
from bothub_nlp_nlu.debug_parse import debug_parse_text as debug_parse_text_core
from bothub_nlp_nlu.sentence_suggestion import (
    sentence_suggestion_text as sentence_suggestion_text_core,
)
from bothub_nlp_nlu.words_distribution import (
    words_distribution_text as words_distribution_core,
)
from bothub_nlp_nlu.train import train_update as train_update_core
from bothub_nlp_nlu.evaluate import evaluate_update as evaluate_update_core


@celery_app.task(name=TASK_NLU_PARSE_TEXT)
def parse_text(repository_version, repository_authorization, *args, **kwargs):
    return parse_text_core(
        repository_version, repository_authorization, *args, **kwargs
    )


@celery_app.task(name=TASK_NLU_DEBUG_PARSE_TEXT)
def debug_parse_text(repository_version, repository_authorization, *args, **kwargs):
    return debug_parse_text_core(
        repository_version, repository_authorization, *args, **kwargs
    )


@celery_app.task(name=TASK_NLU_SENTENCE_SUGGESTION_TEXT)
def sentence_suggestion_text(*args, **kwargs):
    return sentence_suggestion_text_core(*args, **kwargs)


@celery_app.task(name=TASK_NLU_TRAIN_UPDATE)
def train_update(repository_version, by_id, repository_authorization):
    return train_update_core(repository_version, by_id, repository_authorization)


@celery_app.task(name=TASK_NLU_EVALUATE_UPDATE)
def evaluate_update(repository_version, by_id, repository_authorization):
    return evaluate_update_core(repository_version, by_id, repository_authorization)


@celery_app.task(name=TASK_NLU_WORDS_DISTRIBUTION)
def words_distribution(repository_version, language, repository_authorization):
    return words_distribution_core(
        repository_version, language, repository_authorization
    )
