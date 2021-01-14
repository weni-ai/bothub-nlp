import logging
from typing import Any, Dict, List, Text, Tuple, Optional

from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
import numpy as np

from rasa.nlu.utils.hugging_face.hf_transformers import HFTransformersNLP

logger = logging.getLogger(__name__)


class HFTransformersNLPCustom(HFTransformersNLP):
    """Utility Component for interfacing between Transformers library and Rasa OS.
    The transformers(https://github.com/huggingface/transformers) library
    is used to load pre-trained language models like BERT, GPT-2, etc.
    The component also tokenizes and featurizes dense featurizable attributes of each
    message.
    """

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super(HFTransformersNLP, self).__init__(component_config)

        self._load_model()
        self.whitespace_tokenizer = WhitespaceTokenizer()

    def _load_model(self) -> None:
        """Try loading the model"""

        from bothub.shared.utils.rasa_components.registry import (
            model_class_dict,
            model_weights_defaults,
            model_tokenizer_dict,
            from_pt_dict,
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

        try:
            from bothub_nlp_celery.app import nlp_language

            self.tokenizer, self.model = nlp_language
        except TypeError:
            logger.info(
                f"Model could not be retrieved from celery cache "
                f"Loading model {self.model_name} in memory"
            )
            self.tokenizer = model_tokenizer_dict[self.model_name].from_pretrained(
                model_weights_defaults[self.model_name], cache_dir=None
            )
            self.model = model_class_dict[self.model_name].from_pretrained(
                self.model_name,
                cache_dir=None,
                from_pt=from_pt_dict.get(self.model_name, False),
            )

        # Use a universal pad token since all transformer architectures do not have a
        # consistent token. Instead of pad_token_id we use unk_token_id because
        # pad_token_id is not set for all architectures. We can't add a new token as
        # well since vocabulary resizing is not yet supported for TF classes.
        # Also, this does not hurt the model predictions since we use an attention mask
        # while feeding input.
        self.pad_token_id = self.tokenizer.unk_token_id
        logger.debug(f"Loaded Tokenizer and Model for {self.model_name}")

    def _add_lm_specific_special_tokens(
        self, token_ids: List[List[int]]
    ) -> List[List[int]]:
        """Add language model specific special tokens which were used during their training.
        Args:
            token_ids: List of token ids for each example in the batch.
        Returns:
            Augmented list of token ids for each example in the batch.
        """
        from bothub.shared.utils.rasa_components.registry import (
            model_special_tokens_pre_processors,
        )

        augmented_tokens = [
            model_special_tokens_pre_processors[self.model_name](example_token_ids)
            for example_token_ids in token_ids
        ]
        return augmented_tokens

    def _lm_specific_token_cleanup(
        self, split_token_ids: List[int], token_strings: List[Text]
    ) -> Tuple[List[int], List[Text]]:
        """Clean up special chars added by tokenizers of language models.
        Many language models add a special char in front/back of (some) words. We clean up those chars as they are not
        needed once the features are already computed.
        Args:
            split_token_ids: List of token ids received as output from the language model specific tokenizer.
            token_strings: List of token strings received as output from the language model specific tokenizer.
        Returns:
            Cleaned up token ids and token strings.
        """
        from bothub.shared.utils.rasa_components.registry import model_tokens_cleaners

        return model_tokens_cleaners[self.model_name](split_token_ids, token_strings)

    def _post_process_sequence_embeddings(
        self, sequence_embeddings: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Compute sentence level representations and sequence level representations for relevant tokens.
        Args:
            sequence_embeddings: Sequence level dense features received as output from language model.
        Returns:
            Sentence and sequence level representations.
        """

        from bothub.shared.utils.rasa_components.registry import (
            model_embeddings_post_processors,
        )

        sentence_embeddings = []
        post_processed_sequence_embeddings = []

        for example_embedding in sequence_embeddings:
            (
                example_sentence_embedding,
                example_post_processed_embedding,
            ) = model_embeddings_post_processors[self.model_name](example_embedding)

            sentence_embeddings.append(example_sentence_embedding)
            post_processed_sequence_embeddings.append(example_post_processed_embedding)

        return (
            np.array(sentence_embeddings),
            np.array(post_processed_sequence_embeddings),
        )
