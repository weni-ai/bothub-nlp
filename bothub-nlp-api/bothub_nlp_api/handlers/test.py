import tornado.web
from tornado import gen
from tornado.gen import Task

from bothub_nlp_celery.actions import ACTION_TEST, queue_name
from bothub_nlp_celery.tasks import TASK_NLU_TEST_UPDATE
from bothub_nlp_celery.app import celery_app
from bothub_nlp import settings as bothub_nlp_settings

from . import ApiHandler
from ..utils import authorization_required


TEST_STATUS_TESTED = 'tested'
TEST_STATUS_FAILED = 'failed'
TEST_STATUS_NOT_READY_FOR_TEST = 'not_ready_for_test'


class TestHandler(ApiHandler):
    @tornado.web.asynchronous
    @gen.engine
    @authorization_required
    def post(self):
        repository_authorization = self.repository_authorization()
        repository = repository_authorization.repository

        languages_report = {}

        for language in bothub_nlp_settings.SUPPORTED_LANGUAGES.keys():
            current_update = repository.current_update(language)

            if not current_update.ready_for_train:
                languages_report[language] = {
                    'status': TEST_STATUS_NOT_READY_FOR_TEST,
                }
                continue

            try:
                test_task = celery_app.send_task(
                    TASK_NLU_TEST_UPDATE,
                    args=[
                        current_update.id,
                        repository_authorization.user.id,
                    ],
                    queue=queue_name(ACTION_TEST, current_update.language))
                test_task.wait()
                languages_report[language] = {
                    'status': TEST_STATUS_TESTED,
                }
            except Exception as e:
                from .. import logger
                logger.exception(e)

                if bothub_nlp_settings.BOTHUB_NLP_SENTRY_CLIENT:
                    yield Task(self.captureException, exc_info=True)

                languages_report[language] = {
                    'status': TEST_STATUS_FAILED,
                    'error': str(e),
                }

        self.finish({
            'SUPPORTED_LANGUAGES': list(
                bothub_nlp_settings.SUPPORTED_LANGUAGES.keys(),
            ),
            'languages_report': languages_report,
        })
