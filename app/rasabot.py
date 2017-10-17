"""This module does trainning bot and process data."""
from multiprocessing import Process
from rasa_nlu.converters import load_rasa_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer, Metadata, Interpreter
from models.models import Bot, Profile
from models.base_models import DATABASE
from utils import INVALID_TOKEN, DB_FAIL, DUPLICATE_SLUG
from slugify import slugify


import uuid

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
    Before trainning your bot, make sure do you have the last model lang file.

    python -m spacy download en

    This version load interpreter on initialization.
    """
    def __init__(self, model_bot=None, trainning=False):
        self.model_bot = model_bot
        if not trainning:
            metadata = Metadata(self.model_bot, None)
            self.interpreter = Interpreter.load(metadata, None)

    def ask(self, question):
        return self.interpreter.parse(question)

    def trainning(self, language, data, auth_token, bot_slug):
        """
        Creates a new trainning for the bot.
        Args:
            language: language that bot will be trained
            data: rasa nlu object
            auth_token: token that bot will be related
            bot_slug: unique name bot (beatiful)
        """

        with DATABASE.execution_context():
            owner = Profile.select().where(Profile.uuid == uuid.UUID(auth_token))
            bot_exist = Bot.select().where(Bot.slug == bot_slug)

        if len(owner) != 1:
            return INVALID_TOKEN

        if len(bot_exist):
            return DUPLICATE_SLUG

        owner = owner.get()
        config = '{"pipeline": "spacy_sklearn", \
                                "path" : "./models", "data" : "./data.json", \
                                "language": "%s"}' % language

        training_data = load_rasa_data(data)
        trainer = Trainer(RasaNLUConfig(config))
        trainer.train(training_data)
        bot_data = trainer.persist()
        bot_slug = slugify(bot_slug)
        with DATABASE.execution_context():
            bot = Bot.create(bot=bot_data, owner=owner, slug=bot_slug)

            bot.save()
            if bot.uuid:
                return dict(uuid=str(bot.uuid), slug=str(bot.slug), owner=bot.owner.uuid.hex)

        logger.error("Fail when try insert new bot")
        return DB_FAIL


class RasaBotProcess(Process):
    """
    This class is instantied when start a process bot and does all data process
    """
    def __init__(self, questions_queue, answers_queue, new_question_event,
                 new_answer_event, model_bot, *args, **kwargs):
        """
        Args:
            questions_queue: queue with question to this bot
            answaers_queue: queue that will be put response after prediction
            new_questions_event: event that will start new prediction
            new_answer_event: event will be dispareted when rasa return prediction
        """
        super().__init__(*args, **kwargs)
        self._bot = None
        self.questions_queue = questions_queue
        self.answers_queue = answers_queue
        self.new_question_event = new_question_event
        self.new_answer_event = new_answer_event
        self.model_bot = model_bot

    def run(self):
        self._bot = RasaBot(self.model_bot)
        while True:
            self.new_question_event.wait()
            self.new_question_event.clear()
            logger.info('A new question arrived!')
            answer = self._bot.ask(self.questions_queue.get())
            self.answers_queue.put(answer)
            self.new_answer_event.set()


class RasaBotTrainProcess(Process):
    """
    This class is instantied when start a process bot to train
    """
    def __init__(self, language, data, callback, auth_token, bot_slug, *args, **kwargs):
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

    def run(self):
        self._bot = RasaBot(trainning=True)
        data = self._bot.trainning(self.language, self.data, self.auth_token, self.bot_slug)
        self.callback(data)
