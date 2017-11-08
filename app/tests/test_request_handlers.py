from server import BotManager, ProfileRequestHandler, BotRequestHandler, BotTrainerRequestHandler, BotInformationsRequestHandler
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

    def get_app(self):
        self.data_training = ""
        with open('tests/training_data_sample.json') as json_data:
            self.data_training = self.data_training.join(json_data.readlines())

        bot_manager = BotManager(gc=False)
        return Application([
            url(r'/auth', ProfileRequestHandler),
            url(r'/bots', BotRequestHandler, {'bot_manager': bot_manager}),
            url(r'/bots/informations', BotInformationsRequestHandler),
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

            response = self.fetch('/train-bot', method='POST', body=self.data_training % ("slug-training", "false"),
                                  headers={'Authorization': 'Bearer 12345678901234567890123456789012'})
            self.assertEqual(json.loads(response.body).get('info', None), INVALID_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/auth', method='POST', body='')
            self.assertEqual(len(json.loads(response.body).get('uuid', None)), 32)
            self.assertEqual(response.code, 200)

            user_token = json.loads(response.body).get('uuid', None)

            response = self.fetch('/train-bot', method='POST', body='',
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body).get('info', None), MISSING_DATA)
            self.assertEqual(response.code, 401)

            response = self.fetch('/train-bot', method='POST', body=self.data_training % ("slug-training", "false"),
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body).get('slug', None), "slug-training")

            response = self.fetch('/train-bot', method='POST', body=self.data_training % ("slug-training", "false"),
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body).get('info', None), DUPLICATE_SLUG)

            response = self.fetch('/train-bot', method='POST', body=self.data_training % ("slug-training-private", "true"),
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body).get('slug', None), "slug-training-private")

    def test_predict_handler(self):
        with test_database(test_db, (Profile, Bot)):
            response = self.fetch('/auth', method='POST', body='')
            self.assertEqual(len(json.loads(response.body).get('uuid', None)), 32)
            self.assertEqual(response.code, 200)

            user_token = json.loads(response.body).get('uuid', None)
            response = self.fetch('/train-bot', method='POST', body=self.data_training % ("slug-predict", "true"),
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(response.code, 200)

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

    def test_information_handler(self):
        with test_database(test_db, (Profile, Bot)):
            response = self.fetch('/auth', method='POST', body='')
            self.assertEqual(len(json.loads(response.body).get('uuid', None)), 32)
            self.assertEqual(response.code, 200)
            user_token = json.loads(response.body).get('uuid', None)

            response = self.fetch('/train-bot', method='POST', body=self.data_training % ("slug-predict-private", "true"),
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(response.code, 200)

            data = {
                'uuid': json.loads(response.body).get('uuid', None)
            }
            response = self.fetch('/bots/informations?%s' % urllib.parse.urlencode(data), method='GET',
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(response.code, 200)

            response = self.fetch('/auth', method='POST', body='')
            self.assertEqual(len(json.loads(response.body).get('uuid', None)), 32)
            self.assertEqual(response.code, 200)
            user_token = json.loads(response.body).get('uuid', None)

            response = self.fetch('/bots/informations?%s' % urllib.parse.urlencode(data), method='GET',
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body).get('info', None), INVALID_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/train-bot', method='POST', body=self.data_training % ("slug-predict-public", "false"),
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(response.code, 200)

            data = {
                'uuid': json.loads(response.body).get('uuid', None)
            }

            response = self.fetch('/bots/informations?%s' % urllib.parse.urlencode(data), method='GET',
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(response.code, 200)


if __name__ == '__main__':
    unittest.main()
