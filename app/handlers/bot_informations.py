""" This module will manage bot informations. """
import uuid

from tornado.web import HTTPError, asynchronous
from tornado.gen import coroutine
from app.handlers.base import BothubBaseHandler
from app.models.models import Bot, Profile
from app.models.base_models import DATABASE
from app.utils import INVALID_TOKEN, token_required, INVALID_BOT, validate_uuid


class BotInformationsRequestHandler(BothubBaseHandler):
    """
    Tornado request handler to get information of specific bot (intents, entities, etc).
    """

    @asynchronous
    @coroutine
    @token_required
    def get(self):
        bot_uuid = self.get_argument('uuid', None)
        if bot_uuid and validate_uuid(bot_uuid):
            with DATABASE.execution_context():
                instance = Bot.select(Bot.uuid, Bot.slug, Bot.intents, Bot.private, Bot.owner)\
                    .where(Bot.uuid == bot_uuid)

                if len(instance):
                    instance = instance.get()
                    information = {
                        'slug': instance.slug,
                        'intents': instance.intents,
                        'private': instance.private
                    }
                    if not instance.private:
                        self.write(information)
                    else:
                        owner_profile = Profile.select().where(
                            Profile.uuid == uuid.UUID(self.get_cleaned_token())).get()
                        if instance.owner == owner_profile:
                            self.write(information)
                        else:
                            raise HTTPError(reason=INVALID_TOKEN, status_code=401)
                    self.finish()
                else:
                    raise HTTPError(reason=INVALID_BOT, status_code=401)
        else:
            raise HTTPError(reason=INVALID_BOT, status_code=401)
