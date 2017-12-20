""" This module will manage the users interactions with your profiles. """
import uuid
import logging

from tornado.web import asynchronous
from tornado.gen import coroutine
from app.handlers.base import BothubBaseHandler
from app.models.base_models import DATABASE
from app.models.models import Repository, RepositoryAuthorization, Profile
from app.settings import DEBUG
from app.utils import token_required


logger = logging.getLogger('bothub NLP - Profile Request Handler')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class ProfileRequestHandler(BothubBaseHandler):
    """
    Tornado request handler to manager profile data.
    """

    @staticmethod
    def _register_profile():
        with DATABASE.execution_context():
            profile = Profile.create()
            profile.save()

        response = dict(uuid=profile.uuid.hex)
        return dict(user=response)

    @asynchronous
    @coroutine
    @token_required
    def get(self):
        if DEBUG:
            logger.info("Consulting a profile...")
        with DATABASE.execution_context():
            owner_profile = Profile.select().where(
                Profile.uuid == uuid.UUID(self.get_cleaned_token()))

            owner_profile = owner_profile.get()
            bots = Repository.select(Repository.uuid, Repository.slug).join(RepositoryAuthorization) \
                                                                      .where(RepositoryAuthorization.profile == owner_profile)
            if bots.exists():
                bots = bots.dicts()

        bots_response = list(map(self._prepare_bot_response, bots))

        self.write(dict(bots=bots_response))
        self.finish()

    @staticmethod
    def _prepare_bot_response(bot):
        bot['uuid'] = str(bot['uuid'])
        return bot

    @asynchronous
    @coroutine
    def post(self):
        if DEBUG:
            logger.info("Recording a new profile...")
        self.write(self._register_profile())
        self.finish()
