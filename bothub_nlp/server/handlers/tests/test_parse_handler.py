import json

from urllib.parse import urlencode
from tornado.testing import AsyncHTTPTestCase
from django.test import TestCase
from rest_framework import status
from bothub.authentication.models import User
from bothub.common.models import Repository
from bothub.common.models import RepositoryAuthorization
from bothub.common import languages

from ....core.train import train_update
from ....core.celery import celery_app

from ....tests.utils import fill_examples
from ....tests.utils import EXAMPLES_MOCKUP


class ParseHandlerTestCase(AsyncHTTPTestCase, TestCase):
    def setUp(self):
        super().setUp()

        celery_app.conf.update(task_always_eager=True)

        self.user = User.objects.create(
            email='fake@user.com',
            nickname='fake')

        self.repository = Repository.objects.create(
            owner=self.user,
            slug='test',
            name='Testing',
            language=languages.LANGUAGE_EN)
        self.authorization = RepositoryAuthorization.objects.create(
            user=self.user,
            repository=self.repository)

    def get_app(self):
        from bothub_nlp.server import make_app
        return make_app()

    def test_method_get(self):
        response = self.fetch(
            '/parse/',
            method='GET',
        )
        self.assertEqual(
            response.code,
            status.HTTP_200_OK)

    def test_valid_request(self):
        fill_examples(EXAMPLES_MOCKUP, self.repository)
        train_update(self.repository.current_update(), self.user)

        text = 'hi, my name is Douglas'

        response = self.fetch(
            '/parse/',
            method='POST',
            body=json.dumps({
                'text': text,
            }),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(
                    self.authorization.uuid),
            },
        )

        self.assertEqual(
            response.code,
            status.HTTP_200_OK)

        content_data = json.loads(response.body)

        self.assertIn(
            'text',
            content_data.keys())
        self.assertEqual(
            content_data.get('text'),
            text)

        self.assertIn(
            'language',
            content_data.keys())

        self.assertIn(
            'update_id',
            content_data.keys())

    def test_valid_request_with_next_lang(self):
        fill_examples(EXAMPLES_MOCKUP, self.repository)
        train_update(self.repository.current_update(), self.user)

        text = 'hi, my name is Douglas'

        response = self.fetch(
            '/parse/',
            method='POST',
            body=json.dumps({
                'text': text,
                'language': 'english'
            }),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(
                    self.authorization.uuid),
            },
        )

        self.assertEqual(
            response.code,
            status.HTTP_200_OK)

        content_data = json.loads(response.body)

        self.assertIn(
            'language',
            content_data.keys())
        self.assertEqual(
            content_data.get('language'),
            languages.LANGUAGE_EN)

    def test_valid_request_method_get(self):
        fill_examples(EXAMPLES_MOCKUP, self.repository)
        train_update(self.repository.current_update(), self.user)

        text = 'hi, my name is Douglas'

        query_string = urlencode({
            'text': text,
        })
        url = '/parse/?{}'.format(query_string)
        response = self.fetch(
            url,
            method='GET',
            headers={
                'Authorization': 'Bearer {}'.format(
                    self.authorization.uuid),
            },
        )

        self.assertEqual(
            response.code,
            status.HTTP_200_OK)

        content_data = json.loads(response.body)

        self.assertIn(
            'text',
            content_data.keys())
        self.assertEqual(
            content_data.get('text'),
            text)

    def test_valid_request_rasa_format(self):
        fill_examples(EXAMPLES_MOCKUP, self.repository)
        train_update(self.repository.current_update(), self.user)

        text = 'hi, my name is Douglas'

        response = self.fetch(
            '/parse/',
            method='POST',
            body=json.dumps({
                'text': text,
                'rasa_format': True,
            }),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(
                    self.authorization.uuid),
            },
        )

        self.assertEqual(
            response.code,
            status.HTTP_200_OK)

        content_data = json.loads(response.body)

        self.assertIn(
            'text',
            content_data.keys())
        self.assertEqual(
            content_data.get('text'),
            text)

        self.assertIn(
            'language',
            content_data.keys())

        self.assertIn(
            'update_id',
            content_data.keys())

        self.assertIn(
            'entities',
            content_data.keys())

        self.assertIn(
            'labels_as_entity',
            content_data.keys())

    def test_bot_not_trained(self):
        text = 'hi, my name is Douglas'

        response = self.fetch(
            '/parse/',
            method='POST',
            body=json.dumps({
                'text': text,
            }),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(
                    self.authorization.uuid),
            },
        )

        self.assertEqual(
            response.code,
            status.HTTP_400_BAD_REQUEST)

        content_data = json.loads(response.body)

        self.assertIn(
            'language',
            content_data.keys())

    def test_without_text(self):
        response = self.fetch(
            '/parse/',
            method='POST',
            body=json.dumps({}),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(
                    self.authorization.uuid),
            },
        )

        self.assertEqual(
            response.code,
            status.HTTP_400_BAD_REQUEST)

    def test_authorization_is_required(self):
        response = self.fetch(
            '/parse/',
            method='POST',
            body=json.dumps({}),
            headers={
                'Content-Type': 'application/json',
            },
        )

        self.assertEqual(
            response.code,
            status.HTTP_401_UNAUTHORIZED)

    def test_language_not_supported(self):
        response = self.fetch(
            '/parse/',
            method='POST',
            body=json.dumps({
                'text': 'මගේ නම ඩග්ලස්',
                'language': 'si',
            }),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(
                    self.authorization.uuid),
            },
        )

        self.assertEqual(
            response.code,
            status.HTTP_400_BAD_REQUEST)

        content_data = json.loads(response.body)

        self.assertIn(
            'language',
            content_data.keys())
