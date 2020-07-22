import json
import unittest
import uuid
import base64
from unittest.mock import patch

from bothub_nlp_nlu_worker.bothub_nlp_nlu.utils import backend
from bothub_nlp_nlu_worker.tests.celery_app import train_update, debug_parse_text


class TestDebugParseTask(unittest.TestCase):

    def setUp(self, *args):
        self.repository_authorization = uuid.uuid4()
        self.current_update = {
            "ready_for_train": True,
            "current_version_id": 6647,
            "repository_authorization_user_id": 303,
            "language": "pt_br",
        }

    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_parse_nlu",
        return_value={
            "version_id": 6647,
            "total_training_end": 4,
            "language": "pt_br",
            "repository_uuid": "e1e8a0fa-625c-4ba3-8b91-4c9f308db791"
        },
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_parse_nlu_persistor",
        return_value={
            "version_id": 49,
            "repository_uuid": "0f6b9644-db55-49a2-a20d-2af74106d892",
            "total_training_end": 3,
            "language": "pt_br",
            "bot_data": base64.b64encode(open('./6647_5_pt_br.tar.gz', 'rb').read())},
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_info",
        return_value={
            "intents": ["affirmative", "negative", "doubt", "bias"]
        },
    )

    def test_debug_parse_without_rasa_format(self, *args):

        result = debug_parse_text(
            self.current_update.get("current_version_id"),
            self.repository_authorization,
            "ok",
        )
        print(json.dumps(result, indent=2))

        self.assertEqual("affirmative", result.get("intent").get("name"))
        self.assertEqual(4, len(result.get("words").get("ok")))

    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_parse_nlu",
        return_value={
            "version_id": 6647,
            "total_training_end": 4,
            "language": "pt_br",
            "repository_uuid": "e1e8a0fa-625c-4ba3-8b91-4c9f308db791"
        },
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_parse_nlu_persistor",
        return_value={
            "version_id": 49,
            "repository_uuid": "0f6b9644-db55-49a2-a20d-2af74106d892",
            "total_training_end": 3,
            "language": "pt_br",
            "bot_data": base64.b64encode(open('./6647_5_pt_br.tar.gz', 'rb').read())},
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_info",
        return_value={
            "intents": ["affirmative", "negative", "doubt", "bias"]
        },
    )
    def test_debug_parse_with_rasa_format(self, *args):

        result = debug_parse_text(
            self.current_update.get("current_version_id"),
            self.repository_authorization,
            "ok",
            True,
        )
        print(json.dumps(result, indent=2))

        self.assertEqual("affirmative", result.get("intent").get("name"))
        self.assertEqual(4, len(result.get("words").get("ok")))
