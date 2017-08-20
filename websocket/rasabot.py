from rasa_nlu.converters import load_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer
from rasa_nlu.model import Metadata, Interpreter


class RasaBot():
    def __init__(self):
        self.data_file = '../etc/spacy/data/demo-rasa.json'
        self.config_file = '../etc/spacy/config.json'
        self.model_dir = '../etc/spacy/models/'

        training_data = load_data(self.data_file)
        trainer = Trainer(RasaNLUConfig(self.config_file))
        trainer.train(training_data)
        model_directory = trainer.persist(self.model_dir)  # Returns the directory the model is stored in
        metadata = Metadata.load(model_directory)   # where model_directory points to the folder the model is persisted in
        self.interpreter = Interpreter.load(metadata, RasaNLUConfig(self.config_file))

    def ask(self, question):
        return self.interpreter.parse(question)
