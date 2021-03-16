from bothub_nlp_celery.app import celery_app

from bothub_nlp_celery.tasks import (
    TASK_NLU_PARSE_TEXT,
    TASK_NLU_EVALUATE_UPDATE,
    TASK_NLU_INTENT_SENTENCE_SUGGESTION_TEXT,
    TASK_NLU_TRAIN_UPDATE,
    TASK_NLU_WORDS_DISTRIBUTION,
    TASK_NLU_DEBUG_PARSE_TEXT,
    TASK_NLU_SENTENCE_SUGGESTION_TEXT,
    TASK_NLU_WORD_SUGGESTION_TEXT,
)

from bothub.shared.utils.backend import backend

from bothub.nlu_worker.task.parse import parse_text
from bothub.nlu_worker.task.debug_parse import debug_parse_text
from bothub.nlu_worker.task.sentence_suggestion import sentence_suggestion_text
from bothub.nlu_worker.task.word_suggestion import word_suggestion_text
from bothub.nlu_worker.task.intent_sentence_suggestion import (
    intent_sentence_suggestion_text,
)
from bothub.nlu_worker.task.words_distribution import words_distribution_text
from bothub.nlu_worker.task.evaluate import evaluate_update

from bothub.shared.evaluate_crossval import evaluate_crossval_update
from bothub.shared.train import train_update

from bothub.nlu_worker.interpreter_manager import InterpreterManager

interpreter_manager = InterpreterManager()


@celery_app.task(name=TASK_NLU_PARSE_TEXT)
def celery_parse_text(repository_version, repository_authorization, *args, **kwargs):
    return parse_text(
        repository_version,
        repository_authorization,
        interpreter_manager,
        *args,
        **kwargs
    )


@celery_app.task(name=TASK_NLU_DEBUG_PARSE_TEXT)
def celery_debug_parse_text(
    repository_version, repository_authorization, *args, **kwargs
):
    return debug_parse_text(
        repository_version,
        repository_authorization,
        interpreter_manager,
        *args,
        **kwargs
    )


@celery_app.task(name=TASK_NLU_SENTENCE_SUGGESTION_TEXT)
def celery_sentence_suggestion_text(*args, **kwargs):
    return sentence_suggestion_text(*args, **kwargs)


@celery_app.task(name=TASK_NLU_INTENT_SENTENCE_SUGGESTION_TEXT)
def celery_intent_sentence_suggestion_text(
    repository_version, repository_authorization, *args, **kwargs
):
    return intent_sentence_suggestion_text(
        repository_version, repository_authorization, *args, **kwargs
    )


@celery_app.task(name=TASK_NLU_WORD_SUGGESTION_TEXT)
def celery_word_suggestion_text(*args, **kwargs):
    return word_suggestion_text(*args, **kwargs)


@celery_app.task(name=TASK_NLU_TRAIN_UPDATE)
def celery_train_update(repository_version, by_id, repository_authorization):
    backend().request_backend_save_queue_id(
        update_id=repository_version,
        repository_authorization=repository_authorization,
        task_id=celery_app.current_task.request.id,
        from_queue=1,
        type_processing=0,
    )
    return train_update(repository_version, by_id, repository_authorization)


@celery_app.task(name=TASK_NLU_EVALUATE_UPDATE)
def celery_evaluate_update(
    repository_version, by_id, repository_authorization, cross_validation
):
    if cross_validation:
        return evaluate_crossval_update(
            repository_version, by_id, repository_authorization, aws_bucket_authentication={}
        )
    return evaluate_update(
        repository_version, repository_authorization, interpreter_manager
    )


@celery_app.task(name=TASK_NLU_WORDS_DISTRIBUTION)
def celery_words_distribution(repository_version, language, repository_authorization):
    return words_distribution_text(
        repository_version, language, repository_authorization
    )
