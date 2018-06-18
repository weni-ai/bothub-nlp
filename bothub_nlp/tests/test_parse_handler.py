import json

from tornado.testing import AsyncHTTPTestCase
from django.test import TestCase
from rest_framework import status
from bothub.authentication.models import User
from bothub.common.models import Repository
from bothub.common.models import RepositoryAuthorization


class ParseHandlerTestCase(AsyncHTTPTestCase, TestCase):
    def setUp(self):
        super().setUp()

        self.user = User.objects.create(
            email='fake@user.com',
            nickname='fake')

        self.repository = Repository.objects.create(
            owner=self.user,
            slug='test',
            name='Testing')
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
