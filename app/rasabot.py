"""This module does trainning bot and process data."""
from multiprocessing import Process
from rasa_nlu.converters import load_rasa_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer
from rasa_nlu.model import Metadata, Interpreter
from models.models import Bot
from models.base_models import DATABASE

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
    def __init__(self, model_dir=None, trainning=False):
        self.model_dir = model_dir
        if not trainning:
            metadata = Metadata(self.model_dir, None)
            self.interpreter = Interpreter.load(metadata, None)

    def ask(self, question):
        return self.interpreter.parse(question)

    def trainning(self, language, data):
        """
        Creates a new trainning for the bot.
        """
        config = '{"pipeline": "spacy_sklearn", \
                                "path" : "./models", "data" : "./data.json", \
                                "language": "%s"}' % language

        training_data = load_rasa_data(data)
        trainer = Trainer(RasaNLUConfig(config))
        trainer.train(training_data)
        bot_data = trainer.persist()
        with DATABASE.execution_context():
            bot = Bot.create(bot=bot_data)
            bot.save()
            if bot.uuid:
                return dict(uuid=str(bot.uuid))
            else:
                logger.error("Fail when try insert new bot")


class RasaBotProcess(Process):
    """
    This class is instantied when start a process bot and does all data process
    """
    def __init__(self, questions_queue, answers_queue, new_question_event,
                 new_answer_event, model_dir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bot = None
        self.questions_queue = questions_queue
        self.answers_queue = answers_queue
        self.new_question_event = new_question_event
        self.new_answer_event = new_answer_event
        self.model_dir = model_dir

    def run(self):
        self._bot = RasaBot(self.model_dir)
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
    def __init__(self, language, data, callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bot = None
        self.language = language
        self.data = data
        self.callback = callback

    def run(self):
        self._bot = RasaBot(trainning=True)
        uuid = self._bot.trainning(self.language, self.data)
        self.callback(uuid)
