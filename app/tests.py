from server import BotManager, ProfileRequestHandler, BotRequestHandler, BotTrainerRequestHandler
from unittest.mock import patch
from playhouse.test_utils import test_database
from peewee import *
from app.models.models import Profile, Bot
from app.utils import *
from tornado import testing
from tornado.web import Application, url

import urllib
import unittest
import json


test_db = SqliteDatabase('tests.db')


class RequestHandlersTest(testing.AsyncHTTPTestCase):
    data_training = """
    {
        "language": "en",
        "slug": "%s",
        "data": {
                "rasa_nlu_data": {
                    "regex_features": [
                    {
                        "name": "zipcode",
                        "pattern": "[0-9]{5}"
                    }
                    ],
                    "entity_synonyms": [
                    {
                        "value": "chinese",
                        "synonyms": ["Chinese", "Chines", "chines"]
                    },
                    {
                        "value": "vegetarian",
                        "synonyms": ["veggie", "vegg"]
                    }
                    ],
                    "common_examples": [
                    {
                        "text": "hey",
                        "intent": "greet",
                        "entities": []
                    },
                    {
                        "text": "howdy",
                        "intent": "greet",
                        "entities": []
                    },
                    {
                        "text": "hey there",
                        "intent": "greet",
                        "entities": []
                    },
                    {
                        "text": "hello",
                        "intent": "greet",
                        "entities": []
                    },
                    {
                        "text": "hi",
                        "intent": "greet",
                        "entities": []
                    },
                    {
                        "text": "good morning",
                        "intent": "greet",
                        "entities": []
                    },
                    {
                        "text": "good evening",
                        "intent": "greet",
                        "entities": []
                    },
                    {
                        "text": "dear sir",
                        "intent": "greet",
                        "entities": []
                    },
                    {
                        "text": "yes",
                        "intent": "affirm",
                        "entities": []
                    },
                    {
                        "text": "yep",
                        "intent": "affirm",
                        "entities": []
                    },
                    {
                        "text": "yeah",
                        "intent": "affirm",
                        "entities": []
                    },
                    {
                        "text": "indeed",
                        "intent": "affirm",
                        "entities": []
                    },
                    {
                        "text": "that's right",
                        "intent": "affirm",
                        "entities": []
                    },
                    {
                        "text": "ok",
                        "intent": "affirm",
                        "entities": []
                    },
                    {
                        "text": "great",
                        "intent": "affirm",
                        "entities": []
                    },
                    {
                        "text": "right,thank you",
                        "intent": "affirm",
                        "entities": []
                    },
                    {
                        "text": "correct",
                        "intent": "affirm",
                        "entities": []
                    },
                    {
                        "text": "great choice",
                        "intent": "affirm",
                        "entities": []
                    },
                    {
                        "text": "sounds really good",
                        "intent": "affirm",
                        "entities": []
                    },
                    {
                        "text": "i'm looking for a place to eat",
                        "intent": "restaurant_search",
                        "entities": []
                    },
                    {
                        "text": "I want to grab lunch",
                        "intent": "restaurant_search",
                        "entities": []
                    },
                    {
                        "text": "I am searching for a dinner spot",
                        "intent": "restaurant_search",
                        "entities": []
                    },
                    {
                        "text": "i'm looking for a place in the north of town",
                        "intent": "restaurant_search",
                        "entities": [
                        {
                            "start": 31,
                            "end": 36,
                            "value": "north",
                            "entity": "location"
                        }
                        ]
                    },
                    {
                        "text": "show me chinese restaurants",
                        "intent": "restaurant_search",
                        "entities": [
                        {
                            "start": 8,
                            "end": 15,
                            "value": "chinese",
                            "entity": "cuisine"
                        }
                        ]
                    },
                    {
                        "text": "show me chines restaurants",
                        "intent": "restaurant_search",
                        "entities": [
                        {
                            "start": 8,
                            "end": 14,
                            "value": "chinese",
                            "entity": "cuisine"
                        }
                        ]
                    },
                    {
                        "text": "show me a mexican place in the centre",
                        "intent": "restaurant_search",
                        "entities": [
                        {
                            "start": 31,
                            "end": 37,
                            "value": "centre",
                            "entity": "location"
                        },
                        {
                            "start": 10,
                            "end": 17,
                            "value": "mexican",
                            "entity": "cuisine"
                        }
                        ]
                    },
                    {
                        "text": "i am looking for an indian spot called olaolaolaolaolaola",
                        "intent": "restaurant_search",
                        "entities": [
                        {
                            "start": 20,
                            "end": 26,
                            "value": "indian",
                            "entity": "cuisine"
                        }
                        ]
                    },    {
                        "text": "search for restaurants",
                        "intent": "restaurant_search",
                        "entities": []
                    },
                    {
                        "text": "anywhere in the west",
                        "intent": "restaurant_search",
                        "entities": [
                        {
                            "start": 16,
                            "end": 20,
                            "value": "west",
                            "entity": "location"
                        }
                        ]
                    },
                    {
                        "text": "anywhere near 18328",
                        "intent": "restaurant_search",
                        "entities": [
                        {
                            "start": 14,
                            "end": 19,
                            "value": "18328",
                            "entity": "location"
                        }
                        ]
                    },
                    {
                        "text": "I am looking for asian fusion food",
                        "intent": "restaurant_search",
                        "entities": [
                        {
                            "start": 17,
                            "end": 29,
                            "value": "asian fusion",
                            "entity": "cuisine"
                        }
                        ]
                    },
                    {
                        "text": "I am looking a restaurant in 29432",
                        "intent": "restaurant_search",
                        "entities": [
                        {
                            "start": 29,
                            "end": 34,
                            "value": "29432",
                            "entity": "location"
                        }
                        ]
                    },
                    {
                        "text": "I am looking for mexican indian fusion",
                        "intent": "restaurant_search",
                        "entities": [
                        {
                            "start": 17,
                            "end": 38,
                            "value": "mexican indian fusion",
                            "entity": "cuisine"
                        }
                        ]
                    },
                    {
                        "text": "central indian restaurant",
                        "intent": "restaurant_search",
                        "entities": [
                        {
                            "start": 0,
                            "end": 7,
                            "value": "central",
                            "entity": "location"
                        },
                        {
                            "start": 8,
                            "end": 14,
                            "value": "indian",
                            "entity": "cuisine"
                        }
                        ]
                    },
                    {
                        "text": "bye",
                        "intent": "goodbye",
                        "entities": []
                    },
                    {
                        "text": "goodbye",
                        "intent": "goodbye",
                        "entities": []
                    },
                    {
                        "text": "good bye",
                        "intent": "goodbye",
                        "entities": []
                    },
                    {
                        "text": "stop",
                        "intent": "goodbye",
                        "entities": []
                    },
                    {
                        "text": "end",
                        "intent": "goodbye",
                        "entities": []
                    },
                    {
                        "text": "farewell",
                        "intent": "goodbye",
                        "entities": []
                    },
                    {
                        "text": "Bye bye",
                        "intent": "goodbye",
                        "entities": []
                    },
                    {
                        "text": "have a good one",
                        "intent": "goodbye",
                        "entities": []
                    }
                    ]
                }
                }
    }
    """

    def get_app(self):
        with patch('requests.get') as mock_get:

            mock_get.text = '127.0.0.1'
            self.bm = BotManager(gc=False)
            return Application([
                url(r'/auth', ProfileRequestHandler),
                url(r'/bots', BotRequestHandler, {'bm': self.bm}),
                url(r'/bots-redirect', BotRequestHandler),
                url(r'/train-bot', BotTrainerRequestHandler)
            ])

    def test_profile_handler(self):
        with test_database(test_db, (Profile, Bot)):
            response = self.fetch('/auth', method='GET')
            self.assertEqual(json.loads(response.body).get('info', None), WRONG_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/auth', method='GET', headers={'Authorization': '1234'})
            self.assertEqual(json.loads(response.body).get('info', None), WRONG_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/auth', method='GET',
                                  headers={'Authorization': 'Bearer 12345678901234567890123456789012'})

            self.assertEqual(json.loads(response.body).get('info', None), INVALID_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/auth', method='POST', body='')
            self.assertEqual(len(json.loads(response.body).get('uuid', None)), 32)
            self.assertEqual(response.code, 200)

            user_token = json.loads(response.body).get('uuid', None)

            response = self.fetch('/auth', method='GET', headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body), [])
            self.assertEqual(response.code, 200)

    def test_training_handler(self):
        with test_database(test_db, (Profile, Bot)):
            response = self.fetch('/train-bot', method='GET')
            self.assertEqual(response.code, 405)

            response = self.fetch('/train-bot', method='POST', body='')
            self.assertEqual(json.loads(response.body).get('info', None), WRONG_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/train-bot', method='POST', body='', headers={'Authorization': '12345'})
            self.assertEqual(json.loads(response.body).get('info', None), WRONG_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/train-bot', method='POST', body='',
                                  headers={'Authorization': 'Bearer 12345678901234567890123456789012'})
            self.assertEqual(json.loads(response.body).get('info', None), MISSING_DATA)
            self.assertEqual(response.code, 401)

            response = self.fetch('/train-bot', method='POST', body=self.data_training,
                                  headers={'Authorization': 'Bearer 12345678901234567890123456789012'})
            self.assertEqual(json.loads(response.body).get('info', None), INVALID_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/auth', method='POST', body='')
            self.assertEqual(len(json.loads(response.body).get('uuid', None)), 32)
            self.assertEqual(response.code, 200)

            user_token = json.loads(response.body).get('uuid', None)

            response = self.fetch('/train-bot', method='POST', body=self.data_training % "slug-training",
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body).get('slug', None), "slug-training")

            response = self.fetch('/train-bot', method='POST', body=self.data_training % "slug-training",
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body).get('info', None), DUPLICATE_SLUG)

    def test_predict_handler(self):
        with test_database(test_db, (Profile, Bot)):
            response = self.fetch('/auth', method='POST', body='')
            self.assertEqual(len(json.loads(response.body).get('uuid', None)), 32)
            self.assertEqual(response.code, 200)

            user_token = json.loads(response.body).get('uuid', None)

            response = self.fetch('/train-bot', method='POST', body=self.data_training % "slug-predict",
                                  headers={'Authorization': 'Bearer %s' % user_token})

            response = self.fetch('/auth', method='GET', headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(response.code, 200)

            data = {
                'uuid': json.loads(response.body)[0].get('uuid', None),
                'msg': 'I want eat chinese food'
            }
            response = self.fetch('/bots?%s' % urllib.parse.urlencode(data), method='GET',
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body).get('bot_uuid', None), data['uuid'])
            self.assertEqual(response.code, 200)

            response = self.fetch('/auth', method='POST', body='')
            self.assertEqual(len(json.loads(response.body).get('uuid', None)), 32)
            self.assertEqual(response.code, 200)

            user_token = json.loads(response.body).get('uuid', None)
            response = self.fetch('/bots?%s' % urllib.parse.urlencode(data), method='GET',
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body).get('info', None), INVALID_TOKEN)
            self.assertEqual(response.code, 401)


if __name__ == '__main__':
    unittest.main()
