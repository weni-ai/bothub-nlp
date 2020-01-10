import unittest

from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.actions import queue_name, ACTION_TRAIN
from bothub_nlp_celery.tasks import TASK_NLU_TRAIN_UPDATE

from bothub_nlp_nlu_worker.bothub_nlp_nlu.utils import backend


class TestTrainTask(unittest.TestCase):
    def setUp(self):
        repository_authorization = ''  # TODO: UUID Integration

        current_update = backend().request_backend_parse(
            router="train", repository_authorization=repository_authorization, language='pt_br'
        )

        self.answer_task = celery_app.send_task(
            TASK_NLU_TRAIN_UPDATE,
            args=[
                current_update.get("current_version_id"),
                current_update.get("repository_authorization_user_id"),
                repository_authorization,
            ],
            queue=queue_name(ACTION_TRAIN, current_update.get("language")),
        )
        self.answer_task.wait()

        self.response = self.answer_task.result

    def test_train_ok(self):
        print(f"Response Train: {self.response}")
