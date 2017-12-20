""" This module will manage bot informations. """
from tornado.web import asynchronous
from tornado.gen import coroutine
from app.handlers.repository_manager import RepositoryManagerHandler
from app.models.models import Repository
from app.models.base_models import DATABASE
from app.settings import ALL_PERMISSIONS
from app.utils import token_required


class BotInformationsRequestHandler(RepositoryManagerHandler):
    """
    Tornado request handler to get information of specific bot (intents, entities, etc).
    """
    allowed_permissions = ALL_PERMISSIONS

    @asynchronous
    @coroutine
    @token_required
    def get(self):
        bot_uuid = self.get_argument('uuid', None)
        self._check_repo_user_authorization(bot_uuid)
        with DATABASE.execution_context():
            instance = Repository.select(Repository.uuid, Repository.slug, Repository.intents, Repository.private)\
                .where(Repository.uuid == bot_uuid).get()

            information = {
                'slug': instance.slug,
                'intents': instance.intents,
                'private': instance.private
            }
        self.write(information)
        self.finish()
