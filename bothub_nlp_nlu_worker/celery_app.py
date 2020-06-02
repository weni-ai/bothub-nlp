from bothub_nlp_celery import settings
from bothub_nlp_celery.actions import send_job_ai_plataform
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_PARSE_TEXT
from bothub_nlp_celery.tasks import TASK_NLU_DEBUG_PARSE_TEXT
from bothub_nlp_celery.tasks import TASK_NLU_SENTENCE_SUGGESTION_TEXT
from bothub_nlp_celery.tasks import TASK_NLU_TRAIN_UPDATE
from bothub_nlp_celery.tasks import TASK_NLU_EVALUATE_UPDATE
from bothub_nlp_celery.tasks import TASK_NLU_WORDS_DISTRIBUTION
from bothub_nlp_rasa_utils import parse, train
from bothub_nlp_rasa_utils import debug_parse
from bothub_nlp_rasa_utils import sentence_suggestion
from bothub_nlp_rasa_utils import evaluate
from bothub_nlp_rasa_utils import words_distribution


@celery_app.task(name=TASK_NLU_PARSE_TEXT)
def parse_text(repository_version, repository_authorization, *args, **kwargs):
    return parse.parse_text(repository_version, repository_authorization, *args, **kwargs)


@celery_app.task(name=TASK_NLU_DEBUG_PARSE_TEXT)
def debug_parse_text(repository_version, repository_authorization, *args, **kwargs):
    return debug_parse.debug_parse_text(repository_version, repository_authorization, *args, **kwargs)


@celery_app.task(name=TASK_NLU_SENTENCE_SUGGESTION_TEXT)
def sentence_suggestion_text(*args, **kwargs):
    return sentence_suggestion.sentence_suggestion_text(*args, **kwargs)


@celery_app.task(name=TASK_NLU_TRAIN_UPDATE)
def train_update(repository_version, by_id, repository_authorization):
    if settings.BOTHUB_NLP_AI_PLATFORM:
        return send_job_ai_plataform(repository_version, by_id, repository_authorization)
    return train.train_update(repository_version, by_id, repository_authorization)


@celery_app.task(name=TASK_NLU_EVALUATE_UPDATE)
def evaluate_update(repository_version, by_id, repository_authorization):
    return evaluate.evaluate_update(repository_version, repository_authorization)


@celery_app.task(name=TASK_NLU_WORDS_DISTRIBUTION)
def words_distribution_update(repository_version, language, repository_authorization):
    return words_distribution.words_distribution_text(repository_version, language, repository_authorization)
