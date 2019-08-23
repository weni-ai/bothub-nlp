# from django.test import TestCase

from ..evaluate import evaluate_update
from ..train import train_update

# from bothub.authentication.models import User
# from bothub.common.models import Repository
# from bothub.common.models import RepositoryEvaluate
# from bothub.common.models import RepositoryEvaluateEntity
# from bothub.common import languages

# from .utils import fill_examples
from .utils import EXAMPLES_MOCKUP


# class EvaluateTestCase(TestCase):

#     def setUp(self):
#         self.user = User.objects.create(
#             email='fake@user.com',
#             nickname='fake')
#         self.repository = Repository.objects.create(
#             owner=self.user,
#             slug='test',
#             name='Testing',
#             language=languages.LANGUAGE_EN)

#     def test_evaluate(self):
#         fill_examples(EXAMPLES_MOCKUP, self.repository)
#         update = self.repository.current_update()
#         train_update(update, self.user)

#         evalute_1 = RepositoryEvaluate.objects.create(
#             repository_update=update,
#             text='hello, my name is Douglas',
#             intent='greet')

#         evalute_2 = RepositoryEvaluate.objects.create(
#             repository_update=update,
#             text='hello',
#             intent='greet')

#         RepositoryEvaluate.objects.create(
#             repository_update=update,
#             text='bye',
#             intent='goodbye')

#         RepositoryEvaluate.objects.create(
#             repository_update=update,
#             text='hey',
#             intent='greet')

#         RepositoryEvaluate.objects.create(
#             repository_update=update,
#             text='test evaluate with rasa and spacy',
#             intent='goodbye')

#         RepositoryEvaluateEntity.objects.create(
#             repository_evaluate=evalute_1,
#             start=18,
#             end=25,
#             entity='name')

#         RepositoryEvaluateEntity.objects.create(
#             repository_evaluate=evalute_2,
#             start=0,
#             end=5,
#             entity='greet')

#         evaluate_update(update, self.user)
