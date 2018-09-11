from tornado.web import asynchronous
from tornado.gen import coroutine

from . import ApiHandler
from ..utils import authorization_required
from ... import settings
from ...core.train import train_update


TRAIN_STATUS_TRAINED = 'trained'
TRAIN_STATUS_FAILED = 'failed'
TRAIN_STATUS_NOT_READY_FOR_TRAIN = 'not_ready_for_train'


class TrainHandler(ApiHandler):
    @asynchronous
    @coroutine
    @authorization_required
    def post(self):
        repository_authorization = self.repository_authorization()
        repository = repository_authorization.repository

        languages_report = {}

        for language in settings.SUPPORTED_LANGUAGES.keys():
            current_update = repository.current_update(language)

            if not current_update.ready_for_train:
                languages_report[language] = {
                    'status': TRAIN_STATUS_NOT_READY_FOR_TRAIN,
                }
                continue

            try:
                train_update(current_update, repository_authorization.user)
                languages_report[language] = {
                    'status': TRAIN_STATUS_TRAINED,
                }
            except Exception as e:  # pragma: no cover
                from .. import logger
                logger.exception(e)  # pragma: no cover
                languages_report[language] = {  # pragma: no cover
                    'status': TRAIN_STATUS_FAILED,
                    'error': str(e),
                }

        self.finish({
            'SUPPORTED_LANGUAGES': list(settings.SUPPORTED_LANGUAGES.keys()),
            'languages_report': languages_report,
        })
