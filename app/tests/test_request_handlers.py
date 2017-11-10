from app.server import BotManager, ProfileRequestHandler, MessageRequestHandler, BotTrainerRequestHandler, BotInformationsRequestHandler
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
        with open('app/tests/training_data_sample.json') as json_data:
            self.data_training = self.data_training.join(json_data.readlines())

        bot_manager = BotManager(gc=False)
        return Application([
            url(r'/v1/auth', ProfileRequestHandler),
            url(r'/v1/message', MessageRequestHandler, {'bot_manager': bot_manager}),
            url(r'/v1/bots', BotInformationsRequestHandler),
            url(r'/v1/bots-redirect', MessageRequestHandler),
            url(r'/v1/train', BotTrainerRequestHandler)
        ])

    def test_profile_handler(self):
        with test_database(test_db, (Profile, Bot)):
            response = self.fetch('/v1/auth', method='GET')
            self.assertEqual(json.loads(response.body).get('info', None), WRONG_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/v1/auth', method='GET', headers={'Authorization': '1234'})
            self.assertEqual(json.loads(response.body).get('info', None), WRONG_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/v1/auth', method='GET',
                                  headers={'Authorization': 'Bearer 12345678901234567890123456789012'})

            self.assertEqual(json.loads(response.body).get('info', None), INVALID_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/v1/auth', method='POST', body='')
            self.assertEqual(len(json.loads(response.body)['user']['uuid']), 32)
            self.assertEqual(response.code, 200)

            user_token = json.loads(response.body)['user']['uuid']

            response = self.fetch('/v1/auth', method='GET', headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body), {"bots": []})
            self.assertEqual(response.code, 200)

    def test_training_handler(self):
        with test_database(test_db, (Profile, Bot)):
            response = self.fetch('/v1/train', method='GET')
            self.assertEqual(response.code, 405)

            response = self.fetch('/v1/train', method='POST', body='')
            self.assertEqual(json.loads(response.body).get('info', None), WRONG_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/v1/train', method='POST', body='', headers={'Authorization': '12345'})
            self.assertEqual(json.loads(response.body).get('info', None), WRONG_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/v1/train', method='POST', body=self.data_training % ("slug-training", "false"),
                                  headers={'Authorization': 'Bearer 12345678901234567890123456789012'})
            self.assertEqual(json.loads(response.body).get('info', None), INVALID_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/v1/auth', method='POST', body='')
            self.assertEqual(len(json.loads(response.body)['user']['uuid']), 32)
            self.assertEqual(response.code, 200)

            user_token = json.loads(response.body)['user']['uuid']

            response = self.fetch('/v1/train', method='POST', body='',
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body).get('info', None), MISSING_DATA)
            self.assertEqual(response.code, 401)

            response = self.fetch('/v1/train', method='POST', body=self.data_training % ("slug-training", "false"),
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body)['bot']['slug'], "slug-training")

            response = self.fetch('/v1/train', method='POST', body=self.data_training % ("slug-training", "false"),
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body).get('info', None), DUPLICATE_SLUG)

            response = self.fetch('/v1/train', method='POST', body=self.data_training % ("slug-training-private", "true"),
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body)['bot']['slug'], "slug-training-private")

    def test_predict_handler(self):
        with test_database(test_db, (Profile, Bot)):
            response = self.fetch('/v1/auth', method='POST', body='')
            self.assertEqual(len(json.loads(response.body)['user']['uuid']), 32)
            self.assertEqual(response.code, 200)

            user_token = json.loads(response.body)['user']['uuid']
            response = self.fetch('/v1/train', method='POST', body=self.data_training % ("slug-predict", "true"),
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(response.code, 200)

            response = self.fetch('/v1/auth', method='GET', headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(response.code, 200)

            data = {
                'bot': json.loads(response.body)['bots'][0]['uuid'],
                'msg': 'I want eat chinese food'
            }
            response = self.fetch('/v1/message?%s' % urllib.parse.urlencode(data), method='GET',
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body)['bot']['uuid'], data['bot'])
            self.assertEqual(response.code, 200)

            response = self.fetch('/v1/auth', method='POST', body='')
            self.assertEqual(len(json.loads(response.body)['user']['uuid']), 32)
            self.assertEqual(response.code, 200)

            user_token = json.loads(response.body)['user']['uuid']
            response = self.fetch('/v1/message?%s' % urllib.parse.urlencode(data), method='GET',
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body).get('info', None), INVALID_TOKEN)
            self.assertEqual(response.code, 401)

    def test_information_handler(self):
        with test_database(test_db, (Profile, Bot)):
            response = self.fetch('/v1/auth', method='POST', body='')
            self.assertEqual(len(json.loads(response.body)['user']['uuid']), 32)
            self.assertEqual(response.code, 200)
            user_token = json.loads(response.body)['user']['uuid']

            response = self.fetch('/v1/train', method='POST', body=self.data_training % ("slug-predict-private", "true"),
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(response.code, 200)

            data = {
                'uuid': json.loads(response.body)['bot']['uuid']
            }
            response = self.fetch('/v1/bots?%s' % urllib.parse.urlencode(data), method='GET',
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(response.code, 200)

            response = self.fetch('/v1/auth', method='POST', body='')
            self.assertEqual(len(json.loads(response.body)['user']['uuid']), 32)
            self.assertEqual(response.code, 200)
            user_token = json.loads(response.body)['user']['uuid']

            response = self.fetch('/v1/bots?%s' % urllib.parse.urlencode(data), method='GET',
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body).get('info', None), INVALID_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/v1/train', method='POST', body=self.data_training % ("slug-predict-public", "false"),
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(response.code, 200)

            data = {
                'uuid': json.loads(response.body)['bot']['uuid']
            }

            response = self.fetch('/v1/bots?%s' % urllib.parse.urlencode(data), method='GET',
                                  headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(response.code, 200)


if __name__ == '__main__':
    unittest.main()
