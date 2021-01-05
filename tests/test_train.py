from unittest import TestCase
from unittest.mock import patch

# from celery_app_test import train_update
from bothub_nlp_rasa_utils import train
import uuid
import os


class TestTrainTask(TestCase):

    # # bert_language = "pt_br"
    bert_language = "en"

    def setUp(self, *args):
        self.repository_authorization = uuid.uuid4()
        self.current_update = {
            "ready_for_train": True,
            "current_version_id": 6647,
            "language": "en",
            "algorithm": "transformer_network_diet_bert",
            "repository_authorization_user_id": 303,
        }

        # change directory to load /models
        # change directory to /tests
        try:
            os.chdir("bothub_nlp_worker")
        except Exception:
            pass
        try:
            os.chdir("nlu_worker")
        except Exception:
            pass

        cur_dir = os.getcwd().split("/")[-1]
        if cur_dir == "tests":
            os.chdir("../")
        print("Current Working Directory ", os.getcwd())

    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_start_training_nlu",
        return_value={
            "language": bert_language,
            "repository_version": 6647,
            "repository_uuid": "e1e8a0fa-625c-4ba3-8b91-4c9f308db791",
            "intent": [],
            "algorithm": "transformer_network_diet_bert",
            "total_training_end": 4,
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_get_examples",
        return_value={
            "count": 358,
            "next": None,
            "previous": None,
            "results": [
                {"text": "ss", "intent": "affirmative", "entities": []},
                {"text": "okay", "intent": "affirmative", "entities": []},
                {"text": "afirmativo", "intent": "affirmative", "entities": []},
                {"text": "okk", "intent": "affirmative", "entities": []},
                {"text": "okayy", "intent": "affirmative", "entities": []},
                {"text": "certo", "intent": "affirmative", "entities": []},
                {"text": "nops", "intent": "negative", "entities": []},
                {"text": "no", "intent": "negative", "entities": []},
                {"text": "nope", "intent": "negative", "entities": []},
                {"text": "não sei", "intent": "doubt", "entities": []},
                {"text": "naa", "intent": "negative", "entities": []},
                {"text": "na", "intent": "negative", "entities": []},
                {"text": "não", "intent": "negative", "entities": []},
                {"text": "talvez nao", "intent": "negative", "entities": []},
                {"text": "nnn", "intent": "negative", "entities": []},
                {"text": "nn", "intent": "negative", "entities": []},
                {"text": "isso", "intent": "affirmative", "entities": []},
                {
                    "text": "sim, preciso daquilo",
                    "intent": "affirmative",
                    "entities": [],
                },
                {"text": "sim, desejo isso", "intent": "affirmative", "entities": []},
                {"text": "sim, quero isso", "intent": "affirmative", "entities": []},
                {"text": "não ne", "intent": "negative", "entities": []},
                {"text": "tenho que pensar", "intent": "doubt", "entities": []},
                {"text": "talvez", "intent": "doubt", "entities": []},
                {"text": "é", "intent": "affirmative", "entities": []},
                {"text": "quero", "intent": "affirmative", "entities": []},
                {"text": "quero sim", "intent": "affirmative", "entities": []},
                {"text": "negativo", "intent": "negative", "entities": []},
                {"text": "siim", "intent": "affirmative", "entities": []},
                {"text": "boa sim", "intent": "affirmative", "entities": []},
            ],
        },
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.send_training_backend_nlu_persistor",
        return_value={},
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_traininglog_nlu",
        return_value={},
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_trainfail_nlu",
        return_value={},
    )
    def test_train_bert(self, *args):
        train.train_update(
            self.current_update.get("current_version_id"),
            self.current_update.get("repository_authorization_user_id"),
            self.repository_authorization,
        )

    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_start_training_nlu",
        return_value={
            "language": "pt_br",
            "repository_version": 6647,
            "repository_uuid": "e1e8a0fa-625c-4ba3-8b91-4c9f308db791",
            "intent": [],
            "algorithm": "transformer_network_diet",
            "total_training_end": 4,
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_get_examples",
        return_value={
            "count": 358,
            "next": None,
            "previous": None,
            "results": [
                {"text": "ss", "intent": "affirmative", "entities": []},
                {"text": "okay", "intent": "affirmative", "entities": []},
                {"text": "afirmativo", "intent": "affirmative", "entities": []},
                {"text": "okk", "intent": "affirmative", "entities": []},
                {"text": "okayy", "intent": "affirmative", "entities": []},
                {"text": "certo", "intent": "affirmative", "entities": []},
                {"text": "nops", "intent": "negative", "entities": []},
                {"text": "no", "intent": "negative", "entities": []},
                {"text": "nope", "intent": "negative", "entities": []},
                {"text": "não sei", "intent": "doubt", "entities": []},
                {"text": "naa", "intent": "negative", "entities": []},
                {"text": "na", "intent": "negative", "entities": []},
                {"text": "não", "intent": "negative", "entities": []},
                {"text": "talvez nao", "intent": "negative", "entities": []},
                {"text": "nnn", "intent": "negative", "entities": []},
            ],
        },
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.send_training_backend_nlu_persistor",
        return_value={},
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_traininglog_nlu",
        return_value={},
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_trainfail_nlu",
        return_value={},
    )
    def test_train_transformer_diet(self, *args):
        train.train_update(
            self.current_update.get("current_version_id"),
            self.current_update.get("repository_authorization_user_id"),
            self.repository_authorization,
        )
