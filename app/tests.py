from server import ProfileRequestHandler, BotRequestHandler, BotTrainerRequestHandler
from playhouse.test_utils import test_database
from peewee import *
from models.models import Profile, Bot
from tornado import testing
from tornado.web import Application, url

import unittest
import settings
import json
import utils


test_db = SqliteDatabase(':memory:')


class RequestHandlersTest(testing.AsyncHTTPTestCase):
    def get_app(self):
        return Application([
            url(r'/auth', ProfileRequestHandler),
            url(r'/bots', BotRequestHandler),
            url(r'/bots-redirect', BotRequestHandler),
            url(r'/train-bot', BotTrainerRequestHandler)
        ])

    def test_profile_handler(self):
        with test_database(test_db, (Profile, Bot)):
            response = self.fetch('/auth', method='GET')
            self.assertEqual(json.loads(response.body).get('info', None), utils.WRONG_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/auth', method='GET', headers={'Authorization': '1234'})
            self.assertEqual(json.loads(response.body).get('info', None), utils.WRONG_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/auth', method='GET',
                                  headers={'Authorization': 'Bearer 12345678901234567890123456789012'})

            self.assertEqual(json.loads(response.body).get('info', None), utils.INVALID_TOKEN)
            self.assertEqual(response.code, 401)

            response = self.fetch('/auth', method='POST', body=b'')
            self.assertEqual(len(json.loads(response.body).get('uuid', None)), 32)
            self.assertEqual(response.code, 200)

            user_token = json.loads(response.body).get('uuid', None)

            response = self.fetch('/auth', method='GET', headers={'Authorization': 'Bearer %s' % user_token})
            self.assertEqual(json.loads(response.body), [])
            self.assertEqual(response.code, 200)


if __name__ == '__main__':
    unittest.main()
