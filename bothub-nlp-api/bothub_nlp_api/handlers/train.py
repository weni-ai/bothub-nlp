import tornado.web
import requests
from tornado import gen
from tornado.gen import Task

from bothub_nlp_celery.actions import ACTION_TRAIN, queue_name
from bothub_nlp_celery.tasks import TASK_NLU_TRAIN_UPDATE
from bothub_nlp_celery.app import celery_app
from bothub_nlp import settings as bothub_nlp_settings

from . import ApiHandler
from ..utils import authorization_required


TRAIN_STATUS_TRAINED = 'trained'
TRAIN_STATUS_FAILED = 'failed'
TRAIN_STATUS_NOT_READY_FOR_TRAIN = 'not_ready_for_train'


class TrainHandler(ApiHandler):
    @tornado.web.asynchronous
    @gen.engine
    @authorization_required
    def post(self):
        repository_authorization = self.repository_authorization_new_backend()
        
        languages_report = {}

        for language in bothub_nlp_settings.SUPPORTED_LANGUAGES.keys():
            current_update = requests.get(
                'http://7cfc350e.ngrok.io/v2/repository/nlp/authorization/train/{}/?language={}'.format(
                    repository_authorization, 
                    language
                )
            ).json()

            if not current_update.get('ready_for_train'):
                languages_report[language] = {
                    'status': TRAIN_STATUS_NOT_READY_FOR_TRAIN,
                }
                continue

            try:
                train_task = celery_app.send_task(
                    TASK_NLU_TRAIN_UPDATE,
                    args=[
                        current_update.get('current_update_id'),
                        current_update.get('repository_authorization_user_id'),
                    ],
                    queue=queue_name(ACTION_TRAIN, current_update.get('language')))
                train_task.wait()
                languages_report[language] = {
                    'status': TRAIN_STATUS_TRAINED,
                }
            except Exception as e:
                from .. import logger
                logger.exception(e)

                if bothub_nlp_settings.BOTHUB_NLP_SENTRY_CLIENT:
                    yield Task(self.captureException, exc_info=True)

                languages_report[language] = {
                    'status': TRAIN_STATUS_FAILED,
                    'error': str(e),
                }

        self.finish({
            'SUPPORTED_LANGUAGES': list(
                bothub_nlp_settings.SUPPORTED_LANGUAGES.keys(),
            ),
            'languages_report': languages_report,
        })
