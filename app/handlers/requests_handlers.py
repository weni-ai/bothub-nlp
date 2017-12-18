#!/usr/bin/env python
""" This module start server """
import traceback

import tornado.ioloop
import tornado.escape
import json
import uuid

from tornado.web import HTTPError, RequestHandler, asynchronous
from tornado.gen import coroutine
from app.rasabot import RasaBotTrainProcess
from app.models.models import Bot, Profile
from app.models.base_models import DATABASE
from app.utils import INVALID_TOKEN, token_required, ERROR_PATTERN, MISSING_DATA, INVALID_BOT, validate_uuid


class BothubBaseHandler(RequestHandler):

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                    'traceback': lines,
                }
            }))
        else:
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                }
            }))


class MessageRequestHandler(BothubBaseHandler):
    """
    Tornado request handler to predict data
    """
    bot_manager = None

    def initialize(self, bot_manager):
        self.bot_manager = bot_manager

    @asynchronous
    @coroutine
    @token_required
    def get(self):
        auth_token = self.request.headers.get('Authorization')[7:]
        bot = self.get_argument('bot', None)
        message = self.get_argument('msg', None)

        if message and bot and validate_uuid(bot):
            answer = self.bot_manager.ask(message, bot, auth_token)
            if answer != (ERROR_PATTERN % INVALID_TOKEN):
                data = {
                    'bot': dict(uuid=bot),
                    'answer': answer
                }
                self.write(data)
                self.finish()
            else:
                raise HTTPError(reason=INVALID_TOKEN, status_code=401)
        else:
            raise HTTPError(reason=MISSING_DATA, status_code=401)


class BotTrainerRequestHandler(BothubBaseHandler):
    """
    Tornado request handler to train bot
    """

    @asynchronous
    @token_required
    def post(self):
        if self.request.body:
            json_body = tornado.escape.json_decode(self.request.body)
            auth_token = self.request.headers.get('Authorization')[7:]
            language = json_body.get("language", None)
            bot_slug = json_body.get("slug", None)
            data = json.dumps(json_body.get("data", None))
            private = json_body.get("private", False)

            bot = RasaBotTrainProcess(language, data, self.callback, auth_token, bot_slug, private)
            bot.daemon = True
            bot.start()
        else:
            raise HTTPError(reason=MISSING_DATA, status_code=401)

    def callback(self, data):
        if isinstance(data, HTTPError):
            self.set_status(data.status_code, data.reason)
            self.write_error(data.status_code)
            return

        self.write(data)
        self.finish()


class ProfileRequestHandler(BothubBaseHandler):
    """
    Tornado request handler to predict data
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
        with DATABASE.execution_context():
            owner_profile = Profile.select().where(
                Profile.uuid == uuid.UUID(self.request.headers.get('Authorization')[7:]))

            owner_profile = owner_profile.get()
            bots = Bot.select(Bot.uuid, Bot.slug).where(Bot.owner == owner_profile).dicts()

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
        self.write(self._register_profile())
        self.finish()


class BotInformationsRequestHandler(BothubBaseHandler):
    """
    Tornado request handler to get information of specific bot (intents, entities, etc)
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
                            Profile.uuid == uuid.UUID(self.request.headers.get('Authorization')[7:])).get()
                        if instance.owner == owner_profile:
                            self.write(information)
                        else:
                            raise HTTPError(reason=INVALID_TOKEN, status_code=401)
                    self.finish()
                else:
                    raise HTTPError(reason=INVALID_BOT, status_code=401)
        else:
            raise HTTPError(reason=INVALID_BOT, status_code=401)
