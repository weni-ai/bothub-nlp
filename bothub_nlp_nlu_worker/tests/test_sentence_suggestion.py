import unittest
from bothub_nlp_nlu_worker.tests.celery_app import sentence_suggestion_text
from bothub_nlp_nlu_worker.bothub_nlp_nlu.sentence_suggestion import SentenceSuggestion
from random import Random


class TestSentenceSuggestionTask(unittest.TestCase):
    def setUp(self, *args):
        self.sentences = [
            "eu quero andar na rua com tranquilidade",
            "meu marido bateu em mim e não sei se falo com meus pais",
            "gostaria de retirar um boleto na agencia mais proxima",
            "aonde eu consigo mais informações sobre o serviço de voces?",
            "como posso acessar o portal da empresa?",
            "meu marido bateu em mim e não sei se falo com meus pais",
            "asdij askdjasd jjzxkcj sakdjiodas asdas",
            "carro",
        ]
        self.seed = "my bothub test"
        self.n = 10

    def test_sentence_suggestion(self, *args):
        for i in range(self.n):
            random = Random((self.seed, i))
            for sentence in self.sentences:
                n = random.randint(1, 20)
                percentage_to_replace = random.random()
                result = sentence_suggestion_text(sentence, percentage_to_replace, n)
                self.assertLessEqual(len(result.get("suggested_sentences")), n)

    def test_similar_words_json(self, *args):
        for sentence in self.sentences:
            sentence_suggestion = SentenceSuggestion()
            similar_words_json = sentence_suggestion.similar_words_json(sentence)
            self.assertEqual(
                list(similar_words_json), list(range(len(sentence.split(" "))))
            )
            for idx in similar_words_json:
                if len(similar_words_json[idx].get("similar_words")) != 0:
                    for similar_word in similar_words_json[idx].get("similar_words"):
                        self.assertIn(
                            similar_words_json[idx].get("type"),
                            sentence_suggestion.to_replace_tags,
                        )
                        self.assertEqual(
                            similar_word.get("type"),
                            similar_words_json[idx].get("type"),
                        )

    def test_get_words_to_replace_idx(self, *args):
        similar_words_json_mock = {
            "0": {"word": "meu", "type": "DET", "similar_words": []},
            "1": {
                "word": "marido",
                "type": "NOUN",
                "similar_words": [
                    {"word": "pai", "type": "NOUN", "relevance": "0.7507466"}
                ],
            },
            "2": {
                "word": "bateu",
                "type": "VERB",
                "similar_words": [
                    {"word": "bate", "type": "VERB", "relevance": "0.58616245"},
                    {"word": "chutou", "type": "VERB", "relevance": "0.61660427"},
                    {"word": "bater", "type": "VERB", "relevance": "0.60553896"},
                    {"word": "batendo", "type": "VERB", "relevance": "0.56993055"},
                    {"word": "bateram", "type": "VERB", "relevance": "0.5649973"},
                ],
            },
            "3": {"word": "em", "type": "ADP", "similar_words": []},
            "4": {
                "word": "mim",
                "type": "NOUN",
                "similar_words": [
                    {"word": "ded\u00e9u", "type": "NOUN", "relevance": "0.4332077"},
                    {"word": "voltemo-nos", "type": "NOUN", "relevance": "0.4346493"},
                    {
                        "word": "irrit\u00e1-la",
                        "type": "NOUN",
                        "relevance": "0.4306215",
                    },
                ],
            },
            "5": {"word": "e", "type": "CCONJ", "similar_words": []},
            "6": {
                "word": "n\u00e3o",
                "type": "ADV",
                "similar_words": [
                    {"word": "nao", "type": "ADV", "relevance": "0.5145442"},
                    {
                        "word": "\u2014n\u00e3o",
                        "type": "ADV",
                        "relevance": "0.43348014",
                    },
                    {"word": "dificilmente", "type": "ADV", "relevance": "0.4153902"},
                ],
            },
            "7": {
                "word": "sei",
                "type": "VERB",
                "similar_words": [
                    {"word": "entendo", "type": "VERB", "relevance": "0.6051379"},
                    {"word": "sabe", "type": "VERB", "relevance": "0.5632819"},
                    {"word": "percebo", "type": "VERB", "relevance": "0.5713719"},
                    {"word": "saberia", "type": "VERB", "relevance": "0.5543314"},
                    {"word": "sabia", "type": "VERB", "relevance": "0.5372125"},
                ],
            },
            "8": {"word": "se", "type": "SCONJ", "similar_words": []},
            "9": {
                "word": "falo",
                "type": "NOUN",
                "similar_words": [
                    {"word": "falei", "type": "NOUN", "relevance": "0.61763376"},
                    {"word": "escrevo", "type": "NOUN", "relevance": "0.5049424"},
                ],
            },
            "10": {"word": "com", "type": "ADP", "similar_words": []},
            "11": {"word": "meus", "type": "DET", "similar_words": []},
            "12": {"word": "pais", "type": "SYM", "similar_words": []},
        }
        text = "meu marido bateu em mim e não sei se falo com meus pais"
        sentence_suggestion = SentenceSuggestion()
        words_to_replace_idx = sentence_suggestion.get_words_to_replace_idx(
            similar_words_json_mock, text.split(" "), 1
        )
        self.assertEqual(["1", "2", "4", "6", "7", "9"], words_to_replace_idx)

    def test_most_similar(self, *args):
        random = Random(self.seed)
        sentence_suggestion = SentenceSuggestion()
        for sentence in self.sentences:
            for word in sentence.split(" "):
                sentence_suggestion.most_similar(word, topn=random.randint(1, 20))
