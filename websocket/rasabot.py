import time
from hashlib import sha1
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


if __name__ == '__main__':
    bot = RasaBot('../etc/spacy/config.json')
    bot.trainning('../etc/spacy/data/demo-rasa.json', '../etc/spacy/models/')
    # Only the first question that have a big delay about 3 seconds.  The questions following have a milliseconds delay.
    start_time = time.time()
    print(bot.ask('Hi'))
    print('=' * 80)
    print(time.time() - start_time)

    # second question
    start_time = time.time()
    print(bot.ask('Hey there!'))
    print('=' * 80)
    print(time.time() - start_time)
    start_time = time.time()
