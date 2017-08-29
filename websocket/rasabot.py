"""This module does trainning bot and process data."""

import os
import uuid

from multiprocessing import Process
from rasa_nlu.converters import load_data
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
    def __init__(self, config_file=None, model_dir=None, data_file=None, trainning=False):
        self.data_file = data_file
        self.model_dir = model_dir
        self.config_file = config_file
        if not trainning:
            metadata = Metadata.load(self.model_dir)
            self.interpreter = Interpreter.load(metadata, RasaNLUConfig(self.config_file))

    def ask(self, question):
        return self.interpreter.parse(question)

    def trainning(self, language, data):
        '''
        Creates a new trainning for the bot.
        This method only makes a new training if the .trainning_hash file does not
        exist, or, if the data_file hash is changed.

        When force is True we force a new trainning.
        Even though there is already one for the current data file.
        '''

        bot_uuid = uuid.uuid4()
        bot_path = "../etc/spacy/%s" % bot_uuid
        if not os.path.exists(bot_path):
            os.makedirs(bot_path)
            os.makedirs("%s/model" % bot_path)

            self.model_dir = "%s/model" % bot_path
            self.config_file = "%s/config.json" % bot_path
            self.data_file = "%s/data.json" % bot_path

            with open(self.data_file, 'w') as data_file, open(self.config_file, 'w') as config_file:
                config_file.write('{"pipeline": "spacy_sklearn", "path" : "./models", "data" : "./data.json", "language": "%s"}' % language)

                data_file.write(data)

            model_dir = Path(self.model_dir)
            data_file = Path(self.data_file)
            training_data = load_data(data_file)
            trainer = Trainer(RasaNLUConfig(self.config_file))
            trainer.train(training_data)
            trainer.persist(model_dir)
            return dict(uuid=str(bot_uuid))


class RasaBotProcess(Process):
    '''
    This class is instantied when start a process bot and does all data process
    '''
    def __init__(self, questions_queue, answers_queue, new_question_event, new_answer_event,
                 rasa_config, model_dir, data_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bot = None
        self.questions_queue = questions_queue
        self.answers_queue = answers_queue
        self.new_question_event = new_question_event
        self.new_answer_event = new_answer_event
        self.rasa_config = rasa_config
        self.model_dir = model_dir
        self.data_file = data_file

    def run(self):
        print('run')
        self._bot = RasaBot(self.rasa_config, self.model_dir, self.data_file)
        while True:
            self.new_question_event.wait()
            self.new_question_event.clear()
            print('A new question arrived!')
            answer = self._bot.ask(self.questions_queue.get())
            self.answers_queue.put(answer)
            self.new_answer_event.set()


class RasaBotTrainProcess(Process):
    def __init__(self, train_queue, language, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bot = None
        self.train_queue = train_queue
        self.language = language
        self.data = data

    def run(self):
        self._bot = RasaBot(trainning=True)
        uuid = self._bot.trainning(self.language, self.data)
        self.train_queue.put(uuid)
