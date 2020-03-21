import logging

from rasa.nlu import registry

from .pipeline_components.crf_label_as_entity_extractor import (
    CRFLabelAsEntityExtractor,
)  # NOQA: E501
from .pipeline_components.regex_featurizer_with_labels import RegexFeaturizer
from .pipeline_components.optimized_spacy_nlp_with_labels import SpacyNLP
from .pipeline_components.tokenizer_spacy_with_labels import SpacyTokenizer


logger = logging.getLogger("bothub_nlp_nlu_worker")

registry.component_classes = registry.component_classes + [
    CRFLabelAsEntityExtractor,
    RegexFeaturizer,
    SpacyNLP,
    SpacyTokenizer,
]
registry.registered_components = {c.name: c for c in registry.component_classes}


def register_component_alias(component_name, component_class):
    class OutputClass(component_class):
        name = component_name

    registry.registered_components.update({component_name: OutputClass})


register_component_alias(
    "bothub_nlp.core.pipeline_components.crf_label_as_entity_extractor."
    + "CRFLabelAsEntityExtractor",
    CRFLabelAsEntityExtractor,
)
register_component_alias(
    "bothub_nlp.core.pipeline_components.intent_entity_featurizer_regex."
    + "RegexFeaturizer",
    RegexFeaturizer,
)
register_component_alias(
    "bothub_nlp.core.pipeline_components.spacy_nlp.SpacyNLP", SpacyNLP
)
register_component_alias(
    "bothub_nlp.core.pipeline_components.tokenizer_spacy.SpacyTokenizer", SpacyTokenizer
)
