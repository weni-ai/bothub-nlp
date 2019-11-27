from bothub_nlp_celery.actions import ACTION_PARSE, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_PARSE_TEXT

from bothub_nlp_api import settings
from bothub_nlp_api.utils import AuthorizationIsRequired
from bothub_nlp_api.utils import ValidationError
from bothub_nlp_api.utils import backend
from bothub_nlp_api.utils import get_repository_authorization


def _parse(authorization, text, language, update_id, rasa_format=False):
    from ..utils import NEXT_LANGS

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
            "parse", repository_authorization, language, update_id
        )
    except Exception:
        update = {}

    if not update.get("update"):
        next_languages = NEXT_LANGS.get(language, [])
        for next_language in next_languages:
            update = backend().request_backend_parse(
                "parse", repository_authorization, next_language
            )
            if update.get("update"):
                break

    if not update.get("update"):
        raise ValidationError("This repository has never been trained")

    answer_task = celery_app.send_task(
        TASK_NLU_PARSE_TEXT,
        args=[update.get("update_id"), repository_authorization, text],
        kwargs={"rasa_format": rasa_format},
        queue=queue_name(ACTION_PARSE, update.get("language")),
    )
    answer_task.wait()

    answer = answer_task.result
    answer.update(
        {
            "text": text,
            "update_id": update.get("update_id"),
            "language": update.get("language"),
        }
    )

    return answer
