import unittest
import uuid
import base64
import os
from unittest.mock import patch

from bothub_nlp_nlu_worker.bothub_nlp_nlu.parse import parse_text


class TestParseTask(unittest.TestCase):
    def setUp(self, *args):
        self.repository_authorization = uuid.uuid4()
        self.current_update = {
            "ready_for_train": True,
            "current_version_id": 6647,
            "repository_authorization_user_id": 303,
        }
        self.local_path = os.getcwd()

    # change directory to /tests
    # change directory to /tests
    try:
        os.chdir("bothub_nlp_worker")
    except Exception:
        pass
    try:
        os.chdir("bothub_nlp_nlu_worker")
    except Exception:
        pass
    try:
        os.chdir("tests")
    except Exception:
        pass

    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_parse_nlu_persistor",
        return_value={
            "version_id": 49,
            "repository_uuid": "0f6b9644-db55-49a2-a20d-2af74106d892",
            "total_training_end": 3,
            "language": "pt_br",
            "bot_data": base64.b64encode(
                open("example_generic_language.tar.gz", "rb").read()
            ),
            "from_aws": False,
        },
    )
    def test_parse_without_rasa_format(self, *args):

        parse_text(
            self.current_update.get("current_version_id"),
            self.repository_authorization,
            "ok",
        )

    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_parse_nlu_persistor",
        return_value={
            "version_id": 49,
            "repository_uuid": "0f6b9644-db55-49a2-a20d-2af74106d892",
            "total_training_end": 3,
            "language": "pt_br",
            "bot_data": base64.b64encode(
                open("example_generic_language.tar.gz", "rb").read()
            ),
            "from_aws": False,
        },
    )
    def test_parse_with_rasa_format(self, *args):

        parse_text(
            self.current_update.get("current_version_id"),
            self.repository_authorization,
            "ok",
            True,
        )
