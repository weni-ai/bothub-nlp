from django.test import TestCase

from ..train import train_update

from bothub.authentication.models import User
from bothub.common.models import Repository
from bothub.common.models import RepositoryExampleEntity
from bothub.common import languages

from ...tests.utils import fill_examples
from ...tests.utils import EXAMPLES_MOCKUP
from ...tests.utils import EXAMPLES_WITH_LABEL_MOCKUP


class TrainTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='fake@user.com',
            nickname='fake')
        self.repository = Repository.objects.create(
            owner=self.user,
            slug='test',
            name='Testing',
            language=languages.LANGUAGE_EN)

    def test_train(self):
        fill_examples(EXAMPLES_MOCKUP, self.repository)
        update = self.repository.current_update()
        train_update(update, self.user)

        self.assertEqual(
            update.by.id,
            self.user.id)

        self.assertIsNotNone(update.training_started_at)
        self.assertIsNotNone(update.trained_at)

    def test_train_with_labels(self):
        fill_examples(EXAMPLES_WITH_LABEL_MOCKUP, self.repository)
        update = self.repository.current_update()
        train_update(update, self.user)

        self.assertEqual(
            update.by.id,
            self.user.id)

        self.assertIsNotNone(update.training_started_at)
        self.assertIsNotNone(update.trained_at)

    def test_train_mixed(self):
        fill_examples([
            {
                'text': 'I love cat',
                'intent': '',
                'entities': [
                    {
                        'start': 7,
                        'end': 10,
                        'entity': 'cat',
                        'label': 'animal',
                    },
                ],
            },
            {
                'text': 'I love dog and cat',
                'intent': '',
                'entities': [
                    {
                        'start': 7,
                        'end': 10,
                        'entity': 'dog',
                    },
                    {
                        'start': 15,
                        'end': 18,
                        'entity': 'cat',
                        'label': 'animal',
                    },
                ],
            },
        ], self.repository)
        update = self.repository.current_update()
        train_update(update, self.user)
