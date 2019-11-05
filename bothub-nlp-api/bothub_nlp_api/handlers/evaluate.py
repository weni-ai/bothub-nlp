from bothub_nlp_celery.actions import ACTION_EVALUATE, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_EVALUATE_UPDATE

from .. import settings
from ..utils import AuthorizationIsRequired
from ..utils import NEXT_LANGS
from ..utils import ValidationError, get_repository_authorization
from ..utils import backend

EVALUATE_STATUS_EVALUATED = "evaluated"
EVALUATE_STATUS_FAILED = "failed"


def evaluate_handler(authorization, language):
    if language and (
        language not in settings.SUPPORTED_LANGUAGES.keys()
        and language not in NEXT_LANGS.keys()
    ):
        raise ValidationError("Language '{}' not supported by now.".format(language))

    repository_authorization = get_repository_authorization(authorization)
    if not repository_authorization:
        raise AuthorizationIsRequired()

    try:
        update = backend().request_backend_parse(
            "evaluate", repository_authorization, language
        )
    except Exception:
        update = {}

    if not update.get("update"):
        raise ValidationError("This repository has never been trained")

    try:
        evaluate_task = celery_app.send_task(
            TASK_NLU_EVALUATE_UPDATE,
            args=[
                update.get("update_id"),
                update.get("user_id"),
                repository_authorization,
            ],
            queue=queue_name(ACTION_EVALUATE, update.get("language")),
        )
        evaluate_task.wait()
        evaluate = evaluate_task.result
        evaluate_report = {
            "language": language,
            "status": EVALUATE_STATUS_EVALUATED,
            "update_id": update.get("update_id"),
            "evaluate_id": evaluate.get("id"),
            "evaluate_version": evaluate.get("version"),
        }
    except Exception as e:
        from .. import logger

        logger.exception(e)

        evaluate_report = {"status": EVALUATE_STATUS_FAILED, "error": str(e)}

    return evaluate_report
