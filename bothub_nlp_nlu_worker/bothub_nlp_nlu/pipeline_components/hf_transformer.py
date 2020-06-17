import logging
from typing import Any, Dict, List, Text, Tuple, Optional

from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.training_data import Message, TrainingData
from rasa.nlu.tokenizers.tokenizer import Token
import rasa.utils.train_utils as train_utils
import numpy as np

from rasa.nlu.constants import (
    TEXT,
    LANGUAGE_MODEL_DOCS,
    DENSE_FEATURIZABLE_ATTRIBUTES,
    TOKEN_IDS,
    TOKENS,
    SENTENCE_FEATURES,
    SEQUENCE_FEATURES,
)

logger = logging.getLogger(__name__)


class HFTransformersNLP(Component):
    """Utility Component for interfacing between Transformers library and Rasa OS.

    The transformers(https://github.com/huggingface/transformers) library
    is used to load pre-trained language models like BERT, GPT-2, etc.
    The component also tokenizes and featurizes dense featurizable attributes of each
    message.
    """

    defaults = {
        # name of the language model to load.
        "model_name": "bert",
        # Pre-Trained weights to be loaded(string)
        "model_weights": None,
        # an optional path to a specific directory to download
        # and cache the pre-trained model weights.
        "cache_dir": None,
    }

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super(HFTransformersNLP, self).__init__(component_config)

        self._load_model()
        self.whitespace_tokenizer = WhitespaceTokenizer()

    def _load_model(self) -> None:
        """Try loading the model"""

        from rasa.nlu.utils.hugging_face.registry import (
            model_class_dict,
            model_weights_defaults,
            model_tokenizer_dict,
        )

        self.model_name = self.component_config["model_name"]

        if self.model_name not in model_class_dict:
            raise KeyError(
                f"'{self.model_name}' not a valid model name. Choose from "
                f"{str(list(model_class_dict.keys()))}or create"
                f"a new class inheriting from this class to support your model."
            )

        self.model_weights = self.component_config["model_weights"]
        self.cache_dir = self.component_config["cache_dir"]

        if not self.model_weights:
            logger.info(
                f"Model weights not specified. Will choose default model weights: "
                f"{model_weights_defaults[self.model_name]}"
            )
            self.model_weights = model_weights_defaults[self.model_name]

        logger.debug(f"Loading Tokenizer and Model for {self.model_name}")

        self.tokenizer = model_tokenizer_dict[self.model_name].from_pretrained(
            self.model_weights, cache_dir=self.cache_dir
        )
        self.model = model_class_dict[self.model_name].from_pretrained(
            self.model_weights, cache_dir=self.cache_dir
        )

        # Use a universal pad token since all transformer architectures do not have a
        # consistent token. Instead of pad_token_id we use unk_token_id because
        # pad_token_id is not set for all architectures. We can't add a new token as
        # well since vocabulary resizing is not yet supported for TF classes.
        # Also, this does not hurt the model predictions since we use an attention mask
        # while feeding input.
        self.pad_token_id = self.tokenizer.unk_token_id
