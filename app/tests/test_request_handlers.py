import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bothub.settings')
django.setup()

import unittest  # noqa: E402
import json  # noqa: E402
import uuid  # noqa: E402

from tornado.testing import AsyncHTTPTestCase  # noqa: E402
from django.test import TestCase  # noqa: E402

from bothub.authentication.models import User  # noqa: E402
from bothub.common import languages  # noqa: E402
from bothub.common.models import Repository  # noqa: E402
from bothub.common.models import RepositoryExample  # noqa: E402
from bothub.common.models import RepositoryExampleEntity  # noqa: E402
from bothub.common.models import RepositoryAuthorization  # noqa: E402

from app.core.train import train_update  # noqa: E402


EXAMPLES_MOCKUP = [
    {
        'text': 'hey',
        'intent': 'greet',
    },
    {
        'text': 'hey there',
        'intent': 'greet',
    },
    {
        'text': 'hello',
        'intent': 'greet',
    },
    {
        'text': 'hi',
        'intent': 'greet',
    },
    {
        'text': 'hello, my name is Douglas',
        'intent': 'greet',
        'entities': [
            {
                'start': 18,
                'end': 25,
                'entity': 'name',
            },
        ]
    },
    {
        'text': 'hi, my name is Douglas',
        'intent': 'greet',
        'entities': [
            {
                'start': 15,
                'end': 22,
                'entity': 'name',
            },
        ]
    },
    {
        'text': 'my name is Douglas',
        'intent': 'greet',
        'entities': [
            {
                'start': 11,
                'end': 18,
                'entity': 'name',
            },
        ]
    },
    {
        'text': 'bye',
        'intent': 'goodbye',
    },
    {
        'text': 'goodbye',
        'intent': 'goodbye',
    },
    {
        'text': 'good bye',
        'intent': 'goodbye',
    },
]


class RequestHandlersTest(AsyncHTTPTestCase, TestCase):
    def setUp(self):
        super(RequestHandlersTest, self).setUp()

        self.test_language = 'en'

        self.user = User.objects.create(
            email='fake@user.com',
            nick='fake')

        self.repository = Repository.objects.create(
            owner=self.user,
            slug='test',
            name='Testing')
        self.authorization = RepositoryAuthorization.objects.create(
            user=self.user,
            repository=self.repository)

        self.trained_repository = Repository.objects.create(
            owner=self.user,
            slug='test2')
        self.trained_authorization = RepositoryAuthorization.objects.create(
            user=self.user,
            repository=self.trained_repository)

        def fill_examples(repository):
            for example_mockup in EXAMPLES_MOCKUP:
                example = RepositoryExample.objects.create(
                    repository_update=repository.current_update(
                        self.test_language),
                    text=example_mockup.get('text'),
                    intent=example_mockup.get('intent'))
                for entity_mockup in example_mockup.get('entities', []):
                    RepositoryExampleEntity.objects.create(
                        repository_example=example,
                        start=entity_mockup.get('start'),
                        end=entity_mockup.get('end'),
                        entity=entity_mockup.get('entity'))

        fill_examples(self.repository)
        fill_examples(self.trained_repository)

        train_update(
            self.trained_repository.current_update(self.test_language),
            self.user)

    def get_app(self):
        from app.server import make_app
        return make_app()

    def test_train_handler(self):
        response = self.fetch(
            '/v1/train',
            method='POST',
            headers={
                'Authorization': 'Bearer {}'.format(
                    self.authorization.uuid),
            },
            body='language={}'.format(self.test_language))
        self.assertEqual(response.code, 200)

    def test_message_handler(self):
        response = self.fetch(
            '/v1/message',
            method='POST',
            headers={
                'Authorization': 'Bearer {}'.format(
                    self.trained_authorization.uuid),
            },
            body='language={};msg={}'.format(
                self.test_language,
                'hi'))
        content_data = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(
            content_data.get('answer', {}).get('intent', {}).get('name'),
            'greet')

    def test_message_handler_without_authorization(self):
        response = self.fetch(
            '/v1/message',
            method='POST',
            headers={},
            body='language={};msg={}'.format(
                self.test_language,
                'hi'))
        self.assertEqual(response.code, 401)

    def test_message_handler_with_invalid_authorization(self):
        response = self.fetch(
            '/v1/message',
            method='POST',
            headers={'Authorization': 'Bearer {}'.format(uuid.uuid4())},
            body='language={};msg={}'.format(
                self.test_language,
                'hi'))
        self.assertEqual(response.code, 401)

    def test_message_handler_without_msg(self):
        response = self.fetch(
            '/v1/message',
            method='POST',
            headers={
                'Authorization': 'Bearer {}'.format(
                    self.trained_authorization.uuid),
            },
            body='language={}'.format(self.test_language))
        self.assertEqual(response.code, 400)

    def test_message_handler_without_language(self):
        response = self.fetch(
            '/v1/message',
            method='POST',
            headers={
                'Authorization': 'Bearer {}'.format(
                    self.trained_authorization.uuid),
            },
            body='msg={}'.format('hi'))
        self.assertEqual(response.code, 400)

    def test_never_trained(self):
        response = self.fetch(
            '/v1/message',
            method='POST',
            headers={'Authorization': 'Bearer {}'.format(self.authorization.uuid)},
            body='language={};msg={}'.format(languages.LANGUAGE_EN, 'hi'))
        self.assertEqual(response.code, 400)


if __name__ == '__main__':
    unittest.main()
