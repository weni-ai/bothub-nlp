import tornado.web
from tornado import gen

from bothub_nlp_celery.actions import ACTION_EVALUATE, queue_name
from bothub_nlp_celery.tasks import TASK_NLU_EVALUATE_UPDATE
from bothub_nlp_celery.app import celery_app
from bothub_nlp import settings as bothub_nlp_settings

from . import ApiHandler
from ..utils import ValidationError
from ..utils import authorization_required
from ..utils import AuthorizationIsRequired
from ..utils import NEXT_LANGS


EVALUATE_STATUS_EVALUATED = 'evaluated'
EVALUATE_STATUS_FAILED = 'failed'


class EvaluateHandler(ApiHandler):
    @tornado.web.asynchronous
    @gen.engine
    @authorization_required
    def post(self):
        language = self.get_argument('language', default=None)

        if language and (
            language not in bothub_nlp_settings.SUPPORTED_LANGUAGES.keys() and
            language not in NEXT_LANGS.keys()
        ):
            raise ValidationError(
                'Language \'{}\' not supported by now.'.format(language),
                field='language')

        repository_authorization = self.repository_authorization()
        if not repository_authorization:
            raise AuthorizationIsRequired()

        repository = repository_authorization.repository
        update = repository.last_trained_update(language)

        if not update:
            raise ValidationError(
                'This repository has never been trained',
                field='language')

        try:
            evaluate_task = celery_app.send_task(
                TASK_NLU_EVALUATE_UPDATE,
                args=[
                    update.id,
                    repository_authorization.user.id,
                ],
                queue=queue_name(ACTION_EVALUATE, update.language))
            evaluate_task.wait()
            evaluate = evaluate_task.result
            evaluate_report = {
                'language': language,
                'status': EVALUATE_STATUS_EVALUATED,
                'update_id': update.id,
                'evaluate_id': evaluate.get('id'),
                'evaluate_version': evaluate.get('version'),
            }
        except Exception as e:
            from .. import logger
            logger.exception(e)

            evaluate_report = {
                'status': EVALUATE_STATUS_FAILED,
                'error': str(e),
            }

        self.finish(evaluate_report)
