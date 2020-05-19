import io
import logging
import bothub_backend
import contextvars
from tempfile import mkdtemp
from decouple import config
from rasa.nlu import components
from rasa.nlu.config import RasaNLUModelConfig

from rasa.nlu.model import Interpreter
from .persistor import BothubPersistor


def backend():
    return bothub_backend.get_backend(
        "bothub_backend.bothub.BothubBackend",
        config("BOTHUB_ENGINE_URL", default="https://api.bothub.it"),
    )


def add_whitespace_tokenizer():
    return {"name": "WhitespaceTokenizer"}


def add_preprocessing(update):
    return {
        "name": "bothub_nlp_nlu.pipeline_components.preprocessing.Preprocessing",
        "language": update.get("language"),
    }


def add_countvectors_featurizer(update):
    if update.get("use_analyze_char"):
        return {
            "name": "CountVectorsFeaturizer",
            "analyzer": "char",
            "min_ngram": 3,
            "max_ngram": 3,
            "token_pattern": "(?u)\\b\\w+\\b",
        }

    else:
        return {"name": "CountVectorsFeaturizer", "token_pattern": "(?u)\\b\\w+\\b"}


def transformer_network_diet_config(update):
    pipeline = []

    # Preprocessing
    pipeline.append(add_preprocessing(update))
    # Tokenizer
    pipeline.append(add_whitespace_tokenizer())
    # Featurizer
    pipeline.append(add_countvectors_featurizer(update))
    # Intent Classifier
    pipeline.append(
        {"name": "DIETClassifier", "entity_recognition": "False", "BILOU_flag": "False"}
    )
    return pipeline


def old_internal_config():
    pipeline = []

    # Tokenizer
    pipeline.append(add_whitespace_tokenizer())
    # Featurizer
    pipeline.append(add_countvectors_featurizer())
    # Intent Classifier
    pipeline.append(
        {
            "name": "DIETClassifier",
            "hidden_layers_sizes": {"text": [256, 128]},
            "number_of_transformer_layers": 0,
            "weight_sparsity": 0,
            "intent_classification": "True",
            "entity_recognition": "False",
            "use_masked_language_model": "False",
            "BILOU_flag": "False",
        }
    )
    return pipeline


def transformer_network_diet_word_embedding_config(update):
    pipeline = []

    # Preprocessing
    pipeline.append(add_preprocessing(update))

    # Language Model
    pipeline.append({"name": "SpacyNLP"})

    # Tokenizer
    pipeline.append({"name": "SpacyTokenizer"})
    # Featurizer
    pipeline.append({"name": "SpacyFeaturizer"})

    # Featurizer
    pipeline.append(add_countvectors_featurizer(update))
    # Intent Classifier
    pipeline.append(
        {"name": "DIETClassifier", "entity_recognition": "False", "BILOU_flag": "False"}
    )

    return pipeline


def bert_config(language):
    pipeline = []

    pipeline.append(add_preprocessing(language))
    # NLP
    pipeline.append(
        {
            "name": "bothub_nlp_nlu.pipeline_components.HFTransformerNLP.HFTransformersNLP",
            "model_name": "bert_portuguese",
        }
    )
    # Tokenizer
    pipeline.append(
        {
            "name": "bothub_nlp_nlu.pipeline_components.lm_tokenizer.LanguageModelTokenizerCustom",
            "intent_tokenization_flag": "False",
            "intent_split_symbol": "_",
        }
    )
    # Featurizer
    featurizer_component = add_countvectors_featurizer()
    pipeline.append(featurizer_component)

    # Intent Classifier
    pipeline.append(
        {"name": "DIETClassifier", "entity_recognition": "False", "BILOU_flag": "False"}
    )

    return pipeline


def legacy_internal_config(update):
    pipeline = []
    # load spacy
    # tokenizer
    pipeline.append(add_whitespace_tokenizer)
    # featurizer
    pipeline.append(add_countvectors_featurizer(update))
    # intent classifier
    pipeline.append(
        {
            "name": "EmbeddingIntentClassifier",
            "similarity_type": "inner"
            if update.get("use_competing_intents")
            else "cosine",
        }
    )

    return pipeline


def legacy_external_config(update):
    pipeline = []
    # load spacy
    pipeline.append({"name": "SpacyNLP"})
    # tokenizer
    pipeline.append({"name": "SpacyTokenizer"})
    # featurizer
    pipeline.append({"name": "SpacyFeaturizer"})
    # intent classifier
    pipeline.append(
        {
            "name": "EmbeddingIntentClassifier",
            "similarity_type": "inner"
            if update.get("use_competing_intents")
            else "cosine",
        }
    )

    return pipeline


def get_rasa_nlu_config_from_update(update):  # pragma: no cover
    if update.get("algorithm") == "BERT":
        pipeline = bert_config(update)
    elif update.get("algorithm") == "transformer_network_diet":
        pipeline = transformer_network_diet_config(update)
    elif update.get("algorithm") == "transformer_network_diet_word_embedding":
        pipeline = transformer_network_diet_word_embedding_config(update)
    elif update.get("algorithm") == "neural_network_internal":
        pipeline = legacy_internal_config(update)
    elif update.get("algorithm") == "neural_network_external":
        pipeline = legacy_external_config(update)

    # entity extractor
    pipeline.append({"name": "CRFEntityExtractor"})

    # spacy named entity recognition
    if update.get("use_name_entities"):
        pipeline.append({"name": "SpacyEntityExtractor"})

    return RasaNLUModelConfig(
        {"language": update.get("language"), "pipeline": pipeline}
    )


class UpdateInterpreters:
    interpreters = {}

    def get(self, repository_version, repository_authorization, use_cache=True):
        update_request = backend().request_backend_parse_nlu(
            repository_version, repository_authorization
        )

        repository_name = (
            f"{update_request.get('version_id')}_"
            f"{update_request.get('total_training_end')}_"
            f"{update_request.get('language')}"
        )

        interpreter = self.interpreters.get(repository_name)

        if interpreter and use_cache:
            return interpreter
        persistor = BothubPersistor(repository_version, repository_authorization)
        model_directory = mkdtemp()
        persistor.retrieve(str(update_request.get("repository_uuid")), model_directory)
        self.interpreters[repository_name] = Interpreter(
            None, {"language": update_request.get("language")}
        ).load(model_directory, components.ComponentBuilder(use_cache=False))
        return self.get(repository_version, repository_authorization)


class PokeLoggingHandler(logging.StreamHandler):
    def __init__(self, pl, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pl = pl

    def emit(self, record):
        if self.pl.cxt.get(default=None) is self.pl:
            super().emit(record)


class PokeLogging:
    def __init__(self, loggingLevel=logging.DEBUG):
        self.loggingLevel = loggingLevel

    def __enter__(self):
        self.cxt = contextvars.ContextVar(self.__class__.__name__)
        self.cxt.set(self)
        logging.captureWarnings(True)
        self.logger = logging.getLogger()
        self.logger.setLevel(self.loggingLevel)
        self.stream = io.StringIO()
        self.handler = PokeLoggingHandler(self, self.stream)
        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.handler.setLevel(self.loggingLevel)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        return self.stream

    def __exit__(self, *args):
        self.logger.removeHandler(self.logger)


update_interpreters = UpdateInterpreters()


def get_examples_request(update_id, repository_authorization):  # pragma: no cover
    start_examples = backend().request_backend_get_examples(
        update_id, False, None, repository_authorization
    )

    examples = start_examples.get("results")

    page = start_examples.get("next")

    if page:
        while True:
            request_examples_page = backend().request_backend_get_examples(
                update_id, True, page, repository_authorization
            )

            examples += request_examples_page.get("results")

            if request_examples_page.get("next") is None:
                break

            page = request_examples_page.get("next")

    return examples


def get_examples_label_request(update_id, repository_authorization):  # pragma: no cover
    start_examples = backend().request_backend_get_examples_labels(
        update_id, False, None, repository_authorization
    )

    examples_label = start_examples.get("results")

    page = start_examples.get("next")

    if page:
        while True:
            request_examples_page = backend().request_backend_get_examples_labels(
                update_id, True, page, repository_authorization
            )

            examples_label += request_examples_page.get("results")

            if request_examples_page.get("next") is None:
                break

            page = request_examples_page.get("next")

    return examples_label
