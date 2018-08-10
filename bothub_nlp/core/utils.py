import spacy

from tempfile import mkdtemp

from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Interpreter
from rasa_nlu.components import ComponentBuilder

from .persistor import BothubPersistor


def get_rasa_nlu_config_from_update(update):
    return RasaNLUModelConfig({
        'language': update.language,
        'pipeline': [
            {'name': 'bothub_nlp.core.pipeline_components.spacy_nlp.' +
                     'SpacyNLP'},
            {'name': 'bothub_nlp.core.pipeline_components.tokenizer_spacy.' +
                     'SpacyTokenizer'},
            {'name': 'intent_featurizer_spacy'},
            {'name': 'bothub_nlp.core.pipeline_components.' +
                     'intent_entity_featurizer_regex.RegexFeaturizer'},
            {'name': 'ner_crf'},
            {'name': 'ner_synonyms'},
            {'name': 'intent_classifier_sklearn'},
            {'name': 'bothub_nlp.core.pipeline_components.' +
                     'crf_label_as_entity_extractor.' +
                     'CRFLabelAsEntityExtractor'},
        ],
    })


class UpdateInterpreters:
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
        self.interpreters[update.id] = Interpreter.load(
            model_directory,
            ComponentBuilder(use_cache=False))
        return self.get(update)


class SpacyNLPLanguageManager:
    nlps = {}

    def get(self, lang):
        if lang not in self.nlps:
            from . import logger
            logger.info(f'loading {lang} spacy lang model...')
            self.nlps[lang] = spacy.load(lang, parser=False)
        return self.nlps[lang]
