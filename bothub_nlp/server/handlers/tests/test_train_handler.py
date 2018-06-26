import json

from tornado.testing import AsyncHTTPTestCase
from django.test import TestCase
from rest_framework import status
from bothub.authentication.models import User
from bothub.common.models import Repository
from bothub.common.models import RepositoryAuthorization
from bothub.common import languages

from ....tests.utils import fill_examples
from ....tests.utils import EXAMPLES_MOCKUP
from .... import settings
from ..train import TRAIN_STATUS_TRAINED
from ..train import TRAIN_STATUS_NOT_READY_FOR_TRAIN


class TrainHandlerTestCase(AsyncHTTPTestCase, TestCase):
    def setUp(self):
        super().setUp()

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
            '/train/',
            method='GET',
        )

        self.assertEqual(
            response.code,
            status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_valid_request(self):
        fill_examples(EXAMPLES_MOCKUP, self.repository)

        response = self.fetch(
            '/train/',
            method='POST',
            body='',
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
            'SUPPORTED_LANGUAGES',
            content_data.keys())
        self.assertEqual(
            content_data.get('SUPPORTED_LANGUAGES'),
            settings.SUPPORTED_LANGUAGES)

        self.assertIn(
            'languages_report',
            content_data.keys())

        languages_report = content_data.get('languages_report')

        self.assertIn(
            languages_report.get(languages.LANGUAGE_EN).get('status'),
            TRAIN_STATUS_TRAINED)

        self.assertIn(
            languages_report.get(languages.LANGUAGE_PT).get('status'),
            TRAIN_STATUS_NOT_READY_FOR_TRAIN)
