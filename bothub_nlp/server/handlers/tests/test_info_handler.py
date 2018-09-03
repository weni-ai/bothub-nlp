import json

from tornado.testing import AsyncHTTPTestCase
from django.test import TestCase
from rest_framework import status

from bothub.authentication.models import User
from bothub.common.models import Repository
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity
from bothub.common import languages


class InfoHandlerTestCase(AsyncHTTPTestCase, TestCase):
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

    def test_okay(self):
        response = self.fetch(
            '/info/',
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

        self.assertEqual(
            content_data.get('uuid'),
            str(self.repository.uuid))

    def test_repository_with_label(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi')
        example_entity = RepositoryExampleEntity.objects.create(
            repository_example=example,
            start=0,
            end=0,
            entity='hi')
        example_entity.entity.set_label('greet')
        example_entity.entity.save()

        response = self.fetch(
            '/info/',
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

        self.assertEqual(
            content_data.get('uuid'),
            str(self.repository.uuid))
