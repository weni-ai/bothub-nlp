from tempfile import mkdtemp

from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Interpreter

from .persistor import BothubPersistor


def get_rasa_nlu_config_from_update(update):
    return RasaNLUModelConfig({
        'language': update.language,
        'pipeline': 'spacy_sklearn',
    })


class UpdateInterpreters(object):
    interpreters = {}

    def get(self, update):
        interpreter = self.interpreters.get(update.id)
        if interpreter:
            return interpreter
        persistor = BothubPersistor(update)
        model_directory = mkdtemp()
        persistor.retrieve(
            str(update.repository.uuid),
            str(update.id),
            model_directory)
        self.interpreters[update.id] = Interpreter.load(model_directory)
        return self.get(update)
