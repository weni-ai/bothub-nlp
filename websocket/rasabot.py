"""This module does trainning bot and process data."""

import os
import uuid

from multiprocessing import Process
from rasa_nlu.converters import load_rasa_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer
from rasa_nlu.model import Metadata, Interpreter
from unipath import Path


class RasaBot():
    '''
    Before trainning your bot, make sure do you have the last model lang file.

    python -m spacy download en

    This version load interpreter on initialization.
    '''
    def __init__(self, model_dir=None, trainning=False):
        self.model_dir = model_dir
        if not trainning:
            metadata = Metadata(self.model_dir, None)
            self.interpreter = Interpreter.load(metadata, None)

    def ask(self, question):
        return self.interpreter.parse(question)

    def trainning(self, language, data):
        '''
        Creates a new trainning for the bot.
        '''

        bot_uuid = uuid.uuid4()
        bot_path = "../etc/spacy/%s" % bot_uuid
        if not os.path.exists(bot_path):
            os.makedirs(bot_path)
            os.makedirs("%s/model" % bot_path)

            self.model_dir = "%s/model" % bot_path
            config = '{"pipeline": "spacy_sklearn", \
                                   "path" : "./models", "data" : "./data.json", \
                                   "language": "%s"}' % language
            

            model_dir = Path(self.model_dir)
            training_data = load_rasa_data(data)
            trainer = Trainer(RasaNLUConfig(config))
            trainer.train(training_data)
            trainer.persist(model_dir)
            return dict(uuid=str(bot_uuid))


class RasaBotProcess(Process):
    '''
    This class is instantied when start a process bot and does all data process
    '''
    def __init__(self, questions_queue, answers_queue, new_question_event, new_answer_event,
                 model_dir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bot = None
        self.questions_queue = questions_queue
        self.answers_queue = answers_queue
        self.new_question_event = new_question_event
        self.new_answer_event = new_answer_event
        self.model_dir = model_dir

    def run(self):
        print('run')
        self._bot = RasaBot(self.model_dir)
        while True:
            self.new_question_event.wait()
            self.new_question_event.clear()
            print('A new question arrived!')
            answer = self._bot.ask(self.questions_queue.get())
            self.answers_queue.put(answer)
            self.new_answer_event.set()


class RasaBotTrainProcess(Process):
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
