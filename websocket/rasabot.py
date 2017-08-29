from multiprocessing import Process
from rasa_nlu.converters import load_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer
from rasa_nlu.model import Metadata, Interpreter
from unipath import Path
import uuid
import os


class RasaBot():
    '''
    Before trainning your bot, make sure do you have the last model lang file.

    python -m spacy download en

    This version load interpreter on initialization.
    '''
    def __init__(self, config_file, model_dir, data_file, trainning=False):
        self.data_file = data_file
        self.model_dir = model_dir
        self.config_file = config_file
        if not trainning:
            metadata = Metadata.load(self.model_dir)
            self.interpreter = Interpreter.load(metadata, RasaNLUConfig(self.config_file))

    def ask(self, question):
        return self.interpreter.parse(question)

    def trainning(self): # force=False
        '''
        Creates a new trainning for the bot. This method only makes a new training if the .trainning_hash file does not
        exist, or, if the data_file hash is changed.

        When force is True we force a new trainning. Even though there is already one for the current data file.
        '''
        model_dir = Path(self.model_dir)
        data_file = Path(self.data_file)

        bot_uuid = uuid.uuid4()

        if not os.path.exists("../etc/spacy/%s" % bot_uuid):
            os.makedirs("../etc/spacy/%s" % bot_uuid)
        training_data = load_data(data_file)
        trainer = Trainer(RasaNLUConfig(self.config_file))
        trainer.train(training_data)
        trainer.persist(model_dir)


class RasaBotProcess(Process):
    def __init__(self, questions_queue, answers_queue, new_question_event, new_answer_event, rasa_config, model_dir, data_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bot = None
        self.questions_queue = questions_queue
        self.answers_queue = answers_queue
        self.new_question_event = new_question_event
        self.new_answer_event = new_answer_event
        self.rasa_config = rasa_config
        self.model_dir = model_dir
        self.data_file = data_file

    def run(self, *args, **kwargs):
        print('run')
        self._bot = RasaBot(self.rasa_config, self.model_dir, self.data_file)
        while True:
            # This is not the best aproach! But works for now. ;)
            # while self.questions_queue.empty():
            #     time.sleep(0.001)
            self.new_question_event.wait()
            self.new_question_event.clear()
            print('A new question arrived!')
            answer = self._bot.ask(self.questions_queue.get())
            self.answers_queue.put(answer)
            self.new_answer_event.set()
