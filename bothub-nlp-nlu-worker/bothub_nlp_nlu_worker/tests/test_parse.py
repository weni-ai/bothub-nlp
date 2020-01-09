import unittest

from bothub_nlp_celery.actions import ACTION_PARSE, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_PARSE_TEXT

from bothub_nlp_nlu_worker.bothub_nlp_nlu.utils import backend


class TestParseTask(unittest.TestCase):
    def setUp(self):
        text = 'ok'
        language = 'pt_br'

        repository_authorization = ''  # TODO: UUID Integration

        current_update = backend().request_backend_parse(
            router="parse", repository_authorization=repository_authorization, language=language
        )

        self.answer_task = celery_app.send_task(
            TASK_NLU_PARSE_TEXT,
            args=[current_update.get("repository_version"), repository_authorization, text],
            kwargs={"rasa_format": False},
            queue=queue_name(ACTION_PARSE, language),
        )
        self.answer_task.wait()

        self.response = self.answer_task.result

    def test_parse_ok(self):
        print(f"Response Parse: {self.response}")
        self.assertEqual(len(self.response), 5)


