import re
from typing import Any, Optional, Text, Dict, List, Type

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.training_data import Message, TrainingData

from ..preprocessing.preprocessing_factory import PreprocessingFactory


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
    defaults = {"language": None}

    def __init__(
            self,
            component_config: Optional[Dict[Text, Any]] = None,
    ) -> None:
        super(Preprocessing, self).__init__(component_config)
        self.language = self.component_config["language"]


    @classmethod
    def create(
        cls, component_config: Dict[Text, Any], config: RasaNLUModelConfig
    ) -> "Preprocessing":
        return cls(component_config)

    def provide_context(self) -> Dict[Text, Any]:
        return {"language": self.language}

    @staticmethod
    def do_entities_overlap(entities: List[Dict]):
        sorted_entities = sorted(entities, key=lambda e: e["start"])
        for i in range(len(sorted_entities) - 1):
            curr_ent = sorted_entities[i]
            next_ent = sorted_entities[i + 1]
            if (
                    next_ent["start"] < curr_ent["end"]
                    and next_ent["entity"] != curr_ent["entity"]
            ):
                return True
        return False

    @staticmethod
    def remove_overlapping_entities(entities):
        new_entities = []
        for i in range(len(entities)):
            overlap = False
            for j in range(len(entities)):
                if i != j and (entities[i]['start'] >= entities[j]['start'] and entities[i]['end'] <= entities[j]['end']):
                    overlap = True
                elif i != j and ((entities[i]['end'] > entities[j]['start'] and entities[i]['start'] < entities[j]['end']) and not (entities[j]['start'] >= entities[i]['start'] and entities[j]['end'] <= entities[i]['end'])):
                    overlap = True
            if not overlap:
                new_entities.append(entities[i])
        return new_entities

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        """Train this component"""
        not_repeated_phrases = set()
        size = len(training_data.training_examples)
        subtract_idx = 0
        PREPROCESS_FACTORY = PreprocessingFactory().get_preprocess(self.language)

        for idx in range(size):
            example = training_data.training_examples[idx - subtract_idx]

            if 'entities' in example.data and self.do_entities_overlap(example.data['entities']):
                example.data['entities'] = self.remove_overlapping_entities(example.data['entities'])

            example_text = example.text
            example_text = PREPROCESS_FACTORY.preprocess(example_text)

            if example_text in not_repeated_phrases:
                # remove example at this index from training_examples
                training_data.training_examples.pop(idx - subtract_idx)
                subtract_idx += 1
            else:
                not_repeated_phrases.add(example_text)
                training_data.training_examples[idx - subtract_idx].text = example_text

    def process(self, message: Message, **kwargs: Any) -> None:
        """Process an incoming message."""
        APOSTROPHE_OPTIONS = ["'", "`"]

        # remove apostrophe from the phrase (important be first than s_regex regex)
        for APOSTROPHE in APOSTROPHE_OPTIONS:
            message.text = message.text.replace(APOSTROPHE, "")

        PREPROCESS_FACTORY = PreprocessingFactory().get_preprocess(self.language)

        message.text = PREPROCESS_FACTORY.preprocess(message.text)
