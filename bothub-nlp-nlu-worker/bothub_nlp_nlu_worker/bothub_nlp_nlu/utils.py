import io
import logging
from tempfile import mkdtemp
from collections import defaultdict

import bothub_backend
import contextvars
from decouple import config
from rasa.nlu import components
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.model import Interpreter
from rasa.nlu.test import plot_histogram, IntentEvaluationResult, determine_token_labels

from .persistor import BothubPersistor


def backend():
    return bothub_backend.get_backend(
        "bothub_backend.bothub.BothubBackend",
        config("BOTHUB_ENGINE_URL", default="https://api.bothub.it"),
    )


def get_rasa_nlu_config_from_update(update):
    pipeline = []
    if update.get("algorithm") == update.get("ALGORITHM_STATISTICAL_MODEL"):
        pipeline.append({"name": "bothub_nlp_nlu.pipeline_components.optimized_spacy_nlp_with_labels.SpacyNLP"})
        pipeline.append({"name": "bothub_nlp_nlu.pipeline_components.tokenizer_spacy_with_labels.SpacyTokenizer"})
        pipeline.append({"name": "RegexFeaturizer"})
        pipeline.append({"name": "SpacyFeaturizer"})
        pipeline.append({"name": "CRFEntityExtractor"})
        # spacy named entity recognition
        if update.get("use_name_entities"):
            pipeline.append({"name": "SpacyEntityExtractor"})
        pipeline.append({"name": "bothub_nlp_nlu.pipeline_components.crf_label_as_entity_extractor.CRFLabelAsEntityExtractor"})
        pipeline.append({"name": "SklearnIntentClassifier"})
    else:
        use_spacy = update.get("algorithm") == update.get(
            "ALGORITHM_NEURAL_NETWORK_EXTERNAL"
        )
        # load spacy
        pipeline.append({"name": "bothub_nlp_nlu.pipeline_components.optimized_spacy_nlp_with_labels.SpacyNLP"})
        # tokenizer
        pipeline.append({"name": "bothub_nlp_nlu.pipeline_components.tokenizer_spacy_with_labels.SpacyTokenizer"})
        # featurizer
        if use_spacy:
            pipeline.append({"name": "SpacyFeaturizer"})
        else:
            pipeline.append({"name": "CountVectorsFeaturizer"})
        # intent classifier
        pipeline.append(
            {
                "name": "EmbeddingIntentClassifier",
                "similarity_type": "inner"
                if update.get("use_competing_intents")
                else "cosine",
            }
        )

        # entity extractor
        pipeline.append({"name": "CRFEntityExtractor"})
        # spacy named entity recognition
        if update.get("use_name_entities"):
            pipeline.append({"name": "SpacyEntityExtractor"})
        # label extractor
        pipeline.append({"name": "bothub_nlp_nlu.pipeline_components.crf_label_as_entity_extractor.CRFLabelAsEntityExtractor"})
    return RasaNLUModelConfig(
        {"language": update.get("language"), "pipeline": pipeline}
    )


class BothubInterpreter(Interpreter):
    @staticmethod
    def default_output_attributes():
        return {
            "intent": {"name": None, "confidence": 0.0},
            "entities": [],
            "labels_as_entity": [],
        }

    # @classmethod
    # def load(cls, model_dir, component_builder=None, skip_validation=False):
    #     model_metadata = Metadata.load(model_dir)
    #     cls.ensure_model_compatibility(model_metadata)
    #     return cls.create(model_metadata, component_builder, skip_validation)
    #
    # @classmethod
    # def create(cls, model_metadata, component_builder=None, skip_validation=False):
    #     context = {}
    #     if component_builder is None:
    #         component_builder = components.ComponentBuilder()
    #     pipeline = []
    #     if not skip_validation:
    #         components.validate_requirements(model_metadata.component_classes)
    #
    #     for i in range(model_metadata.number_of_components):
    #         component_meta = model_metadata.for_component(i)
    #         component = component_builder.load_component(
    #             component_meta, model_metadata.model_dir, model_metadata, **context
    #         )
    #         try:
    #             updates = component.provide_context()
    #             if updates:
    #                 context.update(updates)
    #             pipeline.append(component)
    #         except components.MissingArgumentError as e:
    #             raise Exception(
    #                 "Failed to initialize component '{}'. "
    #                 "{}".format(component.name, e)
    #             )
    #     return cls(pipeline, context, model_metadata)


class UpdateInterpreters:
    interpreters = {}

    def get(self, update, repository_authorization, use_cache=True):
        update_request = backend().request_backend_parse_nlu(
            update, repository_authorization
        )

        interpreter = self.interpreters.get(update_request.get("update_id"))
        if interpreter and use_cache:
            return interpreter
        persistor = BothubPersistor(update, repository_authorization)
        model_directory = mkdtemp()
        persistor.retrieve(
            str(update_request.get("repository_uuid")),
            # str(update_request.get("update_id")),
            model_directory,
        )
        self.interpreters[update_request.get("update_id")] = BothubInterpreter.load(
            model_directory, components.ComponentBuilder(use_cache=False)
        )
        return self.get(update, repository_authorization)


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



def get_entity_targets(test_data):
    """Extracts entity targets from the test data."""
    return [e.get("entities", []) for e in test_data.training_examples]


def get_intent_targets(test_data):  # pragma: no cover
    """Extracts intent targets from the test data."""
    return [e.get("intent", "") for e in test_data.training_examples]


def plot_intent_confidences(intent_results, intent_hist_filename):
    import matplotlib.pyplot as plt
    # create histogram of confidence distribution, save to file and display
    plt.gcf().clear()
    pos_hist = [
        r.confidence
        for r in intent_results if r.target == r.prediction]

    neg_hist = [
        r.confidence
        for r in intent_results if r.target != r.prediction]

    plot_histogram([pos_hist, neg_hist], intent_hist_filename)


def get_entity_predictions(interpreter, test_data):  # pragma: no cover
    """Runs the model for the test set and extracts entity
    predictions and tokens."""
    from . import logger
    entity_predictions, tokens = [], []
    for e in test_data.training_examples:
        res = interpreter.parse(e.text, only_output_properties=False)
        entity_predictions.append(res.get('entities', []))
        try:
            tokens.append(res["tokens"])
        except KeyError:
            logger.debug("No tokens present, which is fine if you don't have a"
                         " tokenizer in your pipeline")
    return entity_predictions, tokens


def get_intent_predictions(targets, interpreter,
                           test_data):  # pragma: no cover
    """Runs the model for the test set and extracts intent predictions.
        Returns intent predictions, the original messages
        and the confidences of the predictions"""
    intent_results = []
    for e, target in zip(test_data.training_examples, targets):
        res = interpreter.parse(e.text, only_output_properties=False)
        intent_results.append(IntentEvaluationResult(
            target,
            res.get('intent', {}).get('name'),
            res.get('text', {}),
            res.get('intent', {}).get('confidence')))

    return intent_results


def align_entity_predictions(targets, predictions, tokens, extractors):
    """Aligns entity predictions to the message tokens.

    Determines for every token the true label based on the
    prediction targets and the label assigned by each
    single extractor.

    :param targets: list of target entities
    :param predictions: list of predicted entities
    :param tokens: original message tokens
    :param extractors: the entity extractors that should be considered
    :return: dictionary containing the true token labels and token labels
             from the extractors
    """

    true_token_labels = []
    entities_by_extractors = {extractor: [] for extractor in extractors}
    for p in predictions:
        entities_by_extractors[p["extractor"]].append(p)
    extractor_labels = defaultdict(list)
    for t in tokens:
        true_token_labels.append(
                determine_token_labels(t, targets, None))
        for extractor, entities in entities_by_extractors.items():
            extracted = determine_token_labels(t, entities, extractor)
            extractor_labels[extractor].append(extracted)

    return {"target_labels": true_token_labels,
            "extractor_labels": dict(extractor_labels)}


def align_all_entity_predictions(targets, predictions, tokens, extractors):
    """ Aligns entity predictions to the message tokens for the whole dataset
        using align_entity_predictions

    :param targets: list of lists of target entities
    :param predictions: list of lists of predicted entities
    :param tokens: list of original message tokens
    :param extractors: the entity extractors that should be considered
    :return: list of dictionaries containing the true token labels and token
             labels from the extractors
    """

    aligned_predictions = []
    for ts, ps, tks in zip(targets, predictions, tokens):
        aligned_predictions.append(align_entity_predictions(ts, ps, tks,
                                                            extractors))

    return aligned_predictions


def _targets_predictions_from(intent_results):
    return zip(*[(r.intent_target, r.intent_prediction) for r in intent_results])


update_interpreters = UpdateInterpreters()
