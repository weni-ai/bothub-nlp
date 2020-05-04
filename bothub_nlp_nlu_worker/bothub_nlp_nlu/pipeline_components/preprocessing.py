from unidecode import unidecode
import re
from typing import Any, Optional, Text, Dict, List, Type

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.training_data import Message, TrainingData


class Preprocessing(Component):

    # Which components are required by this component.
    # Listed components should appear before the component itself in the pipeline.
    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        """Specify which components need to be present in the pipeline."""

        return []

    # Defines the default configuration parameters of a component
    # these values can be overwritten in the pipeline configuration
    # of the model. The component should choose sensible defaults
    # and should be able to create reasonable results with the defaults.
    defaults = {}

    # Defines what language(s) this component can handle.
    # This attribute is designed for instance method: `can_handle_language`.
    # Default value is None which means it can handle all languages.
    # This is an important feature for backwards compatibility of components.
    language_list = ["pt"]

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        """Train this component"""

        # set regex parameters
        n_regex = r"\b(n|N)\1*\b"
        s_regex = r"\b(s|S)\1*\b"
        # set replace words
        S_WORD = "sim"
        N_WORD = "nao"

        not_repeated_phrases = set()
        size = len(training_data.training_examples)
        subtract_idx = 0

        for idx in range(size):
            example_text = training_data.training_examples[idx - subtract_idx].text
            # removing accent and lowercasing characters
            example_text = unidecode(example_text.lower())
            # replace regex by "sim"
            example_text = re.sub(s_regex, S_WORD, example_text)
            # replace regex by "nao"
            example_text = re.sub(n_regex, N_WORD, example_text)

            if example_text in not_repeated_phrases:
                # remove example at this index from training_examples
                training_data.training_examples.pop(idx - subtract_idx)
                subtract_idx += 1
            else:
                not_repeated_phrases.add(example_text)
                training_data.training_examples[idx - subtract_idx].text = example_text

    def process(self, message: Message, **kwargs: Any) -> None:
        """Process an incoming message."""
        # set regex parameters
        n_regex = r"\b(n|N)\1*\b"
        s_regex = r"\b(s|S)\1*\b"
        # set replace words
        S_WORD = "sim"
        N_WORD = "nao"

        # removing accent and lowercasing characters
        message.text = unidecode(message.text.lower())
        # replace regex by "sim"
        message.text = re.sub(s_regex, S_WORD, message.text)
        # replace regex by "nao"
        message.text = re.sub(n_regex, N_WORD, message.text)
