"""This module does training bot and process data."""
from multiprocessing import Process
from rasa_nlu.converters import load_rasa_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer, Metadata, Interpreter
from tornado.web import HTTPError

from app.models.models import Bot, Profile
from app.models.base_models import DATABASE
from app.utils import DB_FAIL, DUPLICATE_SLUG
from slugify import slugify


import uuid
import json
import logging


logger = logging.getLogger('bothub NLP - RasaBot')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class RasaBot():
    """
    Before training your bot, make sure do you have the last model lang file.

    python -m spacy download en

    This version load interpreter on initialization.
    """
    def __init__(self, model_bot=None):
        self.model_bot = model_bot

    def training(self, language, data, auth_token, bot_slug, private):
        """
        Creates a new training for the bot.
        Args:
            language: language that bot will be trained
            data: rasa nlu object
            auth_token: token that bot will be related
            bot_slug: unique name bot (beatiful)
        """

        logger.info("Start training bot...")
        with DATABASE.execution_context():
            owner = Profile.select().where(Profile.uuid == uuid.UUID(auth_token))
            bot_exist = Bot.select().where(Bot.slug == bot_slug)

        if len(bot_exist):
            return HTTPError(reason=DUPLICATE_SLUG, status_code=401)

        owner = owner.get()
        config = '{"pipeline": "spacy_sklearn", \
                                "path" : "./models", "data" : "./data.json", \
                                "language": "%s"}' % language

        training_data = load_rasa_data(data)
        trainer = Trainer(RasaNLUConfig(config))
        trainer.train(training_data)
        bot_data = trainer.persist()
        bot_slug = slugify(bot_slug)
        intents = []
        common_examples = json.loads(data).get('rasa_nlu_data').get('common_examples')
        for common_example in common_examples:
            if common_example.get('intent') not in intents:
                intents.append(common_example.get('intent'))
        with DATABASE.execution_context():
            bot = Bot.create(bot=bot_data, owner=owner, slug=bot_slug, private=private, intents=intents)

            bot.save()
            if bot.uuid:
                logger.info("Success bot train...")
                return dict(bot=bot.to_dict())

        logger.error("Fail when try insert new bot")
        return HTTPError(reason=DB_FAIL, status_code=401)


class RasaBotTrainProcess(Process):
    """
    This class is instantied when start a process bot to train
    """
    def __init__(self, language, data, callback, auth_token, bot_slug, private, *args, **kwargs):
        """
        Args:
            language: language that bot will be trained
            data: rasa nlu object
            callback: function to callback when and train
            auth_token: token that bot will be related
            bot_slug: unique name bot (beatiful)
        """
        super().__init__(*args, **kwargs)
        self._bot = None
        self.language = language
        self.data = data
        self.auth_token = auth_token
        self.callback = callback
        self.bot_slug = bot_slug
        self.private = private

    def run(self):
        self._bot = RasaBot()
        data = self._bot.training(self.language, self.data, self.auth_token, self.bot_slug, self.private)
        self.callback(data)
