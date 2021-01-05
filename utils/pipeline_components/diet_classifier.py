import rasa.utils.common as common_utils
from rasa.nlu.classifiers.diet_classifier import DIETClassifier
from typing import Any, Dict, List, Text, Tuple, Optional
from rasa.constants import DOCS_URL_TRAINING_DATA_NLU
from rasa.nlu.training_data import TrainingData
from rasa.nlu.tokenizers.tokenizer import Token
from rasa.nlu.components import Component
from rasa.nlu.constants import (
    EXTRACTOR,
    ENTITIES,
    TOKENS_NAMES,
    TEXT,
    NO_ENTITY_TAG,
    ENTITY_ATTRIBUTE_TYPE,
    ENTITY_ATTRIBUTE_GROUP,
    ENTITY_ATTRIBUTE_ROLE,
    ENTITY_ATTRIBUTE_VALUE,
    ENTITY_ATTRIBUTE_CONFIDENCE_TYPE,
    ENTITY_ATTRIBUTE_CONFIDENCE_ROLE,
    ENTITY_ATTRIBUTE_CONFIDENCE_GROUP,
    ENTITY_ATTRIBUTE_START,
    ENTITY_ATTRIBUTE_END,
    INTENT,
)
from rasa.nlu.training_data import Message


class DIETClassifierCustom(DIETClassifier):
    @staticmethod
    def check_correct_entity_annotations(training_data: TrainingData) -> None:
        """Check if entities are correctly annotated in the training data.
        If the start and end values of an entity do not match any start and end values
        of the respected token, we define an entity as misaligned and log a warning.
        Args:
            training_data: The training data.
        """
        for example in training_data.entity_examples:
            entity_boundaries = [
                (entity[ENTITY_ATTRIBUTE_START], entity[ENTITY_ATTRIBUTE_END])
                for entity in example.get(ENTITIES)
            ]
            token_start_positions = [
                t.start for t in example.get(TOKENS_NAMES[TEXT], [])
            ]
            token_end_positions = [t.end for t in example.get(TOKENS_NAMES[TEXT], [])]

            for entity_start, entity_end in entity_boundaries:
                if (
                    entity_start not in token_start_positions
                    or entity_end not in token_end_positions
                ):
                    common_utils.raise_warning(
                        f"Misaligned entity annotation in message '{example.text}' "
                        f"with intent '{example.get(INTENT)}'. Make sure the start and "
                        f"end values of entities in the training data match the token "
                        f"boundaries (e.g. entities don't include trailing whitespaces "
                        f"or punctuation).",
                        docs=DOCS_URL_TRAINING_DATA_NLU,
                    )
                    break
