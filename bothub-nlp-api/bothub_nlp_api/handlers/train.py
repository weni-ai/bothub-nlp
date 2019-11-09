from bothub_nlp_celery.actions import ACTION_TRAIN, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_TRAIN_UPDATE

from .. import settings
from ..utils import backend
from ..utils import get_repository_authorization

TRAIN_STATUS_TRAINED = "trained"
TRAIN_STATUS_FAILED = "failed"
TRAIN_STATUS_NOT_READY_FOR_TRAIN = "not_ready_for_train"


def train_handler(authorization):
    repository_authorization = get_repository_authorization(authorization)

    languages_report = {}

    for language in settings.SUPPORTED_LANGUAGES.keys():

        current_update = backend().request_backend_parse(
            "train", repository_authorization, language
        )

        if not current_update.get("ready_for_train"):
            languages_report[language] = {"status": TRAIN_STATUS_NOT_READY_FOR_TRAIN}
            continue

        try:
            train_task = celery_app.send_task(
                TASK_NLU_TRAIN_UPDATE,
                args=[
                    current_update.get("current_update_id"),
                    current_update.get("repository_authorization_user_id"),
                    repository_authorization,
                ],
                queue=queue_name(ACTION_TRAIN, current_update.get("language")),
            )
            train_task.wait()
            languages_report[language] = {"status": TRAIN_STATUS_TRAINED}
        except Exception as e:
            # from .. import logger
            # logger.exception(e)

            # if settings.BOTHUB_NLP_SENTRY_CLIENT:
            #     yield Task(self.captureException, exc_info=True)

            languages_report[language] = {
                "status": TRAIN_STATUS_FAILED,
                "error": str(e),
            }

    resp = {
        "SUPPORTED_LANGUAGES": list(settings.SUPPORTED_LANGUAGES.keys()),
        "languages_report": languages_report,
    }
    return resp
