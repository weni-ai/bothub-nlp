import time
from hashlib import sha1
from multiprocessing import Process
from rasa_nlu.converters import load_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer
from rasa_nlu.model import Metadata, Interpreter
from unipath import Path


def calc_hash(filename):
    BUF_SIZE = 65536
    hash_sha1 = sha1()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            hash_sha1.update(data)
    return hash_sha1.hexdigest()


class RasaBot():
    '''
    Before trainning your bot, make sure do you have the last model lang file.

    python -m spacy download en
    '''
    def __init__(self, config_file):
        # self.data_file = '../etc/spacy/data/demo-rasa.json'
        # self.config_file = '../etc/spacy/config.json'
        # self.model_dir = '../etc/spacy/models/'
        self.config_file = config_file
        self.interpreter = None

    # def _data_file_modified(self, data_file):
    #     data_file_hash = hash_file(data_file)
    #     with open('')

    def ask(self, question):
        if self.interpreter is None:
            metadata = Metadata.load(self.model_directory)   # where model_directory points to the folder the model is persisted in
            self.interpreter = Interpreter.load(metadata, RasaNLUConfig(self.config_file))
        return self.interpreter.parse(question)

    def trainning(self, data_file, model_dir, force=False):
        '''
        Creates a new trainning for the bot. This method only makes a new training if the .trainning_hash file does not
        exist, or, if the data_file hash is changed.

        When force is True we force a new trainning. Even though there is already one for the current data file.
        '''
        model_dir = Path(model_dir)
        data_file = Path(data_file)
        trainning_hash_file = model_dir.child('.trainning_hash')
        new_trainning = True

        # The data_file has been modified?
        if trainning_hash_file.exists() and not force:
            new_trainning_hash = calc_hash(data_file)
            current_trainning_hash = trainning_hash_file.read_file()
            new_trainning = new_trainning_hash != current_trainning_hash

        if new_trainning or force:
            training_data = load_data(data_file)
            trainer = Trainer(RasaNLUConfig(self.config_file))
            trainer.train(training_data)
            trainer.persist(model_dir)  # Returns the directory the model is stored in
            trainning_hash_file.write_file(calc_hash(data_file))

    @property
    def model_directory(self):
        return '../etc/spacy/models/model_20170820-174910'


class RasaBotV2():
    '''
    Before trainning your bot, make sure do you have the last model lang file.

    python -m spacy download en

    This version load interpreter on initialization.
    '''
    def __init__(self, config_file, model_dir, data_file):
        self.data_file = data_file
        self.model_dir = model_dir
        self.config_file = config_file
        metadata = Metadata.load(self.model_directory)   # where model_directory points to the folder the model is persisted in
        self.interpreter = Interpreter.load(metadata, RasaNLUConfig(self.config_file))

    def ask(self, question):
        return self.interpreter.parse(question)

    def trainning(self, force=False):
        '''
        Creates a new trainning for the bot. This method only makes a new training if the .trainning_hash file does not
        exist, or, if the data_file hash is changed.

        When force is True we force a new trainning. Even though there is already one for the current data file.
        '''
        model_dir = Path(self.model_dir)
        data_file = Path(self.data_file)
        trainning_hash_file = model_dir.child('.trainning_hash')
        new_trainning = True

        # The data_file has been modified?
        if trainning_hash_file.exists() and not force:
            new_trainning_hash = calc_hash(data_file)
            current_trainning_hash = trainning_hash_file.read_file()
            new_trainning = new_trainning_hash != current_trainning_hash

        if new_trainning or force:
            training_data = load_data(data_file)
            trainer = Trainer(RasaNLUConfig(self.config_file))
            trainer.train(training_data)
            trainer.persist(model_dir)  # Returns the directory the model is stored in
            trainning_hash_file.write_file(calc_hash(data_file))

    @property
    def model_directory(self):
        return '../etc/spacy/models/model_20170820-174910'


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
        self._bot = RasaBotV2(self.rasa_config, self.model_dir, self.data_file)
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
