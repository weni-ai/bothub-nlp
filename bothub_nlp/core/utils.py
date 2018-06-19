from rasa_nlu.config import RasaNLUModelConfig


def get_rasa_nlu_config_from_update(update):
    return RasaNLUModelConfig({
        'language': update.language,
        'pipeline': 'spacy_sklearn',
    })
