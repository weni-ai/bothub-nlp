import unittest

from bothub_nlp_nlu_worker.bothub_nlp_nlu.utils import backend
from bothub_nlp_nlu_worker.celery_app import train_update


class TestTrainTask(unittest.TestCase):
    def setUp(self):
        pass

    def test_train(self):
        repository_authorization = '541161f0-76c0-4fec-8f49-9dc1687c099c'
        current_update = backend().request_backend_parse(
            router="train", repository_authorization=repository_authorization, language='pt_br'
        )

        train_update(
            current_update.get("current_version_id"),
            current_update.get("repository_authorization_user_id"),
            repository_authorization)
