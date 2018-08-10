from django.test import TestCase

from bothub.authentication.models import User
from bothub.common.models import Repository
from bothub.common import languages

from ..train import train_update
from ..parse import parse_text
from ...tests.utils import fill_examples
from ...tests.utils import EXAMPLES_MOCKUP
from ...tests.utils import EXAMPLES_WITH_LABEL_MOCKUP


class ParseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='fake@user.com',
            nickname='fake')
        self.repository = Repository.objects.create(
            owner=self.user,
            slug='test',
            name='Testing',
            language=languages.LANGUAGE_EN)
        fill_examples(EXAMPLES_MOCKUP, self.repository)
        self.update = self.repository.current_update()
        train_update(self.update, self.user)

    def test_parse(self):
        example = EXAMPLES_MOCKUP[0]
        response = parse_text(self.update, example.get('text'))

        self.assertEqual(
            response.get('intent', {}).get('name'),
            example.get('intent'))


class ParseWithLabelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='fake@user.com',
            nickname='fake')
        self.repository = Repository.objects.create(
            owner=self.user,
            slug='test',
            name='Testing',
            language=languages.LANGUAGE_EN)
        fill_examples(EXAMPLES_WITH_LABEL_MOCKUP, self.repository)
        self.update = self.repository.current_update()
        train_update(self.update, self.user)

    def test_parse(self):
        example = EXAMPLES_WITH_LABEL_MOCKUP[0]
        response = parse_text(self.update, example.get('text'))

        entities = response.get('entities')
        labels_as_entity = response.get('labels_as_entity', [])
        self.assertEqual(len(entities), len(labels_as_entity))
