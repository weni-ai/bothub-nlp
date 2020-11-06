import unittest
import uuid
import base64
import os
from unittest.mock import patch

from celery_app import evaluate_update


class TestEvaluateTask(unittest.TestCase):
    def setUp(self, *args):
        self.repository_authorization = uuid.uuid4()
        self.current_update = {
            "ready_for_train": True,
            "current_version_id": 6647,
            "repository_authorization_user_id": 303,
        }

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
        "bothub_backend.bothub.BothubBackend.request_backend_start_evaluation",
        return_value=[
            {"text": "nops", "intent": "negative", "entities": []},
            {"text": "nope", "intent": "negative", "entities": []},
            {"text": "nem", "intent": "negative", "entities": []},
            {"text": "no", "intent": "negative", "entities": []},
            {"text": "nn", "intent": "negative", "entities": []},
            {"text": "n", "intent": "negative", "entities": []},
            {"text": "ja namorei", "intent": "affirmative", "entities": []},
            {"text": "já namorei", "intent": "affirmative", "entities": []},
            {"text": "simn", "intent": "affirmative", "entities": []},
            {
                "text": "aceito sim, muito obrigado",
                "intent": "affirmative",
                "entities": [],
            },
            {"text": "sim, quero o documento", "intent": "affirmative", "entities": []},
            {"text": "não posso fazer isso", "intent": "negative", "entities": []},
            {"text": "não gostei", "intent": "negative", "entities": []},
            {"text": "deixa para lá", "intent": "negative", "entities": []},
            {"text": "não inventa história", "intent": "negative", "entities": []},
            {
                "text": "não queria ter que dizer isso",
                "intent": "negative",
                "entities": [],
            },
            {"text": "não gostei daquele dia", "intent": "negative", "entities": []},
            {
                "text": "nem deve ser tão bom assim",
                "intent": "negative",
                "entities": [],
            },
            {"text": "não aceito", "intent": "negative", "entities": []},
            {"text": "nop deixa de onda", "intent": "negative", "entities": []},
            {"text": "melhor nao falar nada", "intent": "negative", "entities": []},
            {"text": "n gosto disso", "intent": "negative", "entities": []},
            {"text": "para com isso, não pode", "intent": "negative", "entities": []},
            {"text": "melhor não", "intent": "negative", "entities": []},
            {"text": "quero mais não", "intent": "negative", "entities": []},
            {"text": "negativo cara", "intent": "negative", "entities": []},
            {"text": "vamo não", "intent": "negative", "entities": []},
            {"text": "vou nem mentir", "intent": "negative", "entities": []},
            {"text": "nem queria dizer isso", "intent": "negative", "entities": []},
            {"text": "funcionou não", "intent": "negative", "entities": []},
            {"text": "nem rola", "intent": "negative", "entities": []},
            {"text": "não posso", "intent": "negative", "entities": []},
            {"text": "não quero", "intent": "negative", "entities": []},
            {"text": "conta comigo", "intent": "affirmative", "entities": []},
            {"text": "sim, preciso de ajuda", "intent": "affirmative", "entities": []},
            {"text": "é, você está certo sim", "intent": "affirmative", "entities": []},
            {"text": "muito bom, aceito", "intent": "affirmative", "entities": []},
            {"text": "sim, gostei disso", "intent": "affirmative", "entities": []},
            {"text": "conte comigo sempre", "intent": "affirmative", "entities": []},
            {"text": "afirmativo", "intent": "affirmative", "entities": []},
            {"text": "ótima ideia, concordo", "intent": "affirmative", "entities": []},
            {"text": "podemos marcar sim", "intent": "affirmative", "entities": []},
            {"text": "quero sim", "intent": "affirmative", "entities": []},
            {"text": "pode contar comigo", "intent": "affirmative", "entities": []},
            {
                "text": "posso sim! me confirma a data",
                "intent": "affirmative",
                "entities": [],
            },
            {
                "text": "claro que estou disponivel",
                "intent": "affirmative",
                "entities": [],
            },
            {"text": "ótima ideia", "intent": "affirmative", "entities": []},
            {
                "text": "seria legal se fossemos",
                "intent": "affirmative",
                "entities": [],
            },
            {"text": "que legal, gosto sim", "intent": "affirmative", "entities": []},
            {"text": "é possivel", "intent": "affirmative", "entities": []},
            {"text": "pode me mandar sim", "intent": "affirmative", "entities": []},
            {"text": "aceito", "intent": "affirmative", "entities": []},
            {"text": "dá sim", "intent": "affirmative", "entities": []},
            {
                "text": "adorei a ideia vamos sim",
                "intent": "affirmative",
                "entities": [],
            },
            {"text": "quero", "intent": "affirmative", "entities": []},
            {"text": "vamos sim", "intent": "affirmative", "entities": []},
            {"text": "claro", "intent": "affirmative", "entities": []},
            {"text": "com certeza", "intent": "affirmative", "entities": []},
            {"text": "estou", "intent": "affirmative", "entities": []},
            {"text": "consigu", "intent": "affirmative", "entities": []},
            {"text": "consigo", "intent": "affirmative", "entities": []},
            {"text": "não tenho", "intent": "negative", "entities": []},
            {"text": "nem tenho", "intent": "negative", "entities": []},
            {"text": "pior que não tenho", "intent": "negative", "entities": []},
            {"text": "não tenho email", "intent": "negative", "entities": []},
            {"text": "voces fazem coroa dentaria ?", "intent": "bias", "entities": []},
            {"text": "o plano inclui ceromero?", "intent": "bias", "entities": []},
            {"text": "e buco maxilar facial?", "intent": "bias", "entities": []},
            {"text": "varias vezes", "intent": "affirmative", "entities": []},
            {"text": "um pouco", "intent": "affirmative", "entities": []},
            {"text": "acho que faço isso", "intent": "doubt", "entities": []},
            {"text": "quero sim", "intent": "affirmative", "entities": []},
            {"text": "Não estou bem hoje", "intent": "negative", "entities": []},
            {"text": "não quero mais isso", "intent": "negative", "entities": []},
            {"text": "não estou namorando", "intent": "negative", "entities": []},
            {"text": "a ta sei", "intent": "affirmative", "entities": []},
            {"text": "Nunca namorei", "intent": "negative", "entities": []},
            {
                "text": "não, como faço para reconhecer?",
                "intent": "negative",
                "entities": [],
            },
            {"text": "mais ou menos, pq?", "intent": "doubt", "entities": []},
            {
                "text": "já mas não foi muito bom",
                "intent": "affirmative",
                "entities": [],
            },
            {"text": "tudo ótimo", "intent": "affirmative", "entities": []},
            {"text": "tudo otimo", "intent": "affirmative", "entities": []},
            {"text": "tudo", "intent": "affirmative", "entities": []},
            {"text": "tudo bem", "intent": "affirmative", "entities": []},
            {"text": "eu estou bem", "intent": "affirmative", "entities": []},
            {"text": "eu estou bem", "intent": "affirmative", "entities": []},
            {"text": "tudo uma merda", "intent": "negative", "entities": []},
            {"text": "tudo horrivel", "intent": "negative", "entities": []},
            {"text": "tudo pessimo", "intent": "negative", "entities": []},
            {
                "text": "eu também estou num relacionamento abusivo",
                "intent": "bias",
                "entities": [],
            },
            {"text": "já", "intent": "affirmative", "entities": []},
            {
                "text": "hoje já estou num relacionamento abusivo",
                "intent": "bias",
                "entities": [],
            },
            {
                "text": "hoje estou num relacionamento abusivo",
                "intent": "bias",
                "entities": [],
            },
            {"text": "nunca passei por isso", "intent": "negative", "entities": []},
            {"text": "as vezes", "intent": "doubt", "entities": []},
            {"text": "sofro abuso emocional", "intent": "bias", "entities": []},
            {
                "text": "to naum... mas ja namorei um porquinho?",
                "intent": "negative",
                "entities": [],
            },
            {"text": "estou namorando", "intent": "affirmative", "entities": []},
            {"text": "to namorando", "intent": "affirmative", "entities": []},
            {"text": "pior que ja", "intent": "affirmative", "entities": []},
            {"text": "entendi", "intent": "affirmative", "entities": []},
            {"text": "não entendi", "intent": "doubt", "entities": []},
            {"text": "eu quero", "intent": "affirmative", "entities": []},
            {"text": "gosto de futebol", "intent": "bias", "entities": []},
            {
                "text": "meu namorado bateu na minha cara",
                "intent": "bias",
                "entities": [],
            },
            {
                "text": "não ne!! meu namorado bateu na minha cara",
                "intent": "bias",
                "entities": [],
            },
            {"text": "eu fui estruprada", "intent": "affirmative", "entities": []},
            {"text": "tenho que pensar", "intent": "doubt", "entities": []},
            {"text": "mais ou menos", "intent": "doubt", "entities": []},
            {"text": "talvez", "intent": "doubt", "entities": []},
            {"text": "nunca", "intent": "negative", "entities": []},
            {"text": "não", "intent": "negative", "entities": []},
            {"text": "tenho", "intent": "affirmative", "entities": []},
            {"text": "meu namorado me bateu", "intent": "bias", "entities": []},
            {"text": "quero", "intent": "affirmative", "entities": []},
            {"text": "não", "intent": "negative", "entities": []},
            {"text": "sim", "intent": "affirmative", "entities": []},
            {"text": "fui agredida", "intent": "bias", "entities": []},
            {"text": "estuprada", "intent": "bias", "entities": []},
            {"text": "tou namorando", "intent": "affirmative", "entities": []},
            {"text": "sim, tou namorando", "intent": "affirmative", "entities": []},
        ],
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
        },
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_create_evaluate_results",
        return_value={"evaluate_id": 1787, "evaluate_version": 189},
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_create_evaluate_results_intent",
        return_value={},
    )
    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_create_evaluate_results_score",
        return_value={},
    )
    def test_evaluate_ok(self, *args):
        result = evaluate_update(
            self.current_update.get("repository_version"),
            self.current_update.get("user_id"),
            self.repository_authorization,
            cross_validation=False
        )

        self.assertEqual(1787, result.get("id"))
        self.assertEqual(189, result.get("version"))
