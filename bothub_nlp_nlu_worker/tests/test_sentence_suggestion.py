import unittest
import json
from bothub_nlp_nlu_worker.tests.celery_app import sentence_suggestion_text
from bothub_nlp_nlu_worker.bothub_nlp_nlu.sentence_suggestion import SentenceSuggestion


class TestSentenceSuggestionTask(unittest.TestCase):
    def test_sentence_suggestion(self, *args):
        text = 'eu quero andar na rua com tranquilidade'
        result = sentence_suggestion_text(text)
        self.assertEqual(len(result.get('suggested_sentences')), 10)

    def test_similar_words_json(self, *args):
        text = 'meu marido bateu em mim e não sei se falo com meus pais'
        sentence_suggestion = SentenceSuggestion(0.3)
        similar_words_json = sentence_suggestion.similar_words_json(text)
        self.assertEqual(list(similar_words_json), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        for idx in similar_words_json:
            if len(similar_words_json[idx].get('similar_words')) != 0:
                for similar_word in similar_words_json[idx].get('similar_words'):
                    self.assertIn(similar_words_json[idx].get('type'), sentence_suggestion.to_replace_tags)
                    self.assertEqual(similar_word.get('type'), similar_words_json[idx].get('type'))

    def test_get_words_to_replace_idx(self, *args):
        similar_words_json_mock = {
            "0": {
                "word": "meu",
                "type": "DET",
                "similar_words": []
            },
            "1": {
                "word": "marido",
                "type": "NOUN",
                "similar_words": [
                    {
                        "word": "pai",
                        "type": "NOUN",
                        "relevance": "0.7507466"
                    }
                ]
            },
            "2": {
                "word": "bateu",
                "type": "VERB",
                "similar_words": [
                    {
                        "word": "bate",
                        "type": "VERB",
                        "relevance": "0.58616245"
                    },
                    {
                        "word": "chutou",
                        "type": "VERB",
                        "relevance": "0.61660427"
                    },
                    {
                        "word": "bater",
                        "type": "VERB",
                        "relevance": "0.60553896"
                    },
                    {
                        "word": "batendo",
                        "type": "VERB",
                        "relevance": "0.56993055"
                    },
                    {
                        "word": "bateram",
                        "type": "VERB",
                        "relevance": "0.5649973"
                    }
                ]
            },
            "3": {
                "word": "em",
                "type": "ADP",
                "similar_words": []
            },
            "4": {
                "word": "mim",
                "type": "NOUN",
                "similar_words": [
                    {
                        "word": "ded\u00e9u",
                        "type": "NOUN",
                        "relevance": "0.4332077"
                    },
                    {
                        "word": "voltemo-nos",
                        "type": "NOUN",
                        "relevance": "0.4346493"
                    },
                    {
                        "word": "irrit\u00e1-la",
                        "type": "NOUN",
                        "relevance": "0.4306215"
                    }
                ]
            },
            "5": {
                "word": "e",
                "type": "CCONJ",
                "similar_words": []
            },
            "6": {
                "word": "n\u00e3o",
                "type": "ADV",
                "similar_words": [
                    {
                        "word": "nao",
                        "type": "ADV",
                        "relevance": "0.5145442"
                    },
                    {
                        "word": "\u2014n\u00e3o",
                        "type": "ADV",
                        "relevance": "0.43348014"
                    },
                    {
                        "word": "dificilmente",
                        "type": "ADV",
                        "relevance": "0.4153902"
                    }
                ]
            },
            "7": {
                "word": "sei",
                "type": "VERB",
                "similar_words": [
                    {
                        "word": "entendo",
                        "type": "VERB",
                        "relevance": "0.6051379"
                    },
                    {
                        "word": "sabe",
                        "type": "VERB",
                        "relevance": "0.5632819"
                    },
                    {
                        "word": "percebo",
                        "type": "VERB",
                        "relevance": "0.5713719"
                    },
                    {
                        "word": "saberia",
                        "type": "VERB",
                        "relevance": "0.5543314"
                    },
                    {
                        "word": "sabia",
                        "type": "VERB",
                        "relevance": "0.5372125"
                    }
                ]
            },
            "8": {
                "word": "se",
                "type": "SCONJ",
                "similar_words": []
            },
            "9": {
                "word": "falo",
                "type": "NOUN",
                "similar_words": [
                    {
                        "word": "falei",
                        "type": "NOUN",
                        "relevance": "0.61763376"
                    },
                    {
                        "word": "escrevo",
                        "type": "NOUN",
                        "relevance": "0.5049424"
                    }
                ]
            },
            "10": {
                "word": "com",
                "type": "ADP",
                "similar_words": []
            },
            "11": {
                "word": "meus",
                "type": "DET",
                "similar_words": []
            },
            "12": {
                "word": "pais",
                "type": "SYM",
                "similar_words": []
            }
        }
        text = 'meu marido bateu em mim e não sei se falo com meus pais'
        sentence_suggestion = SentenceSuggestion(0.3)
        words_to_replace_idx = sentence_suggestion.get_words_to_replace_idx(similar_words_json_mock, text.split(' '))
        self.assertEqual(['4', '1', '2'], words_to_replace_idx)


