import typing
from recognizers_suite import recognize_number, recognize_ordinal, recognize_age, recognize_currency, \
    recognize_dimension, recognize_temperature, recognize_datetime, recognize_phone_number, recognize_email
from recognizers_suite import Culture, ModelResult

from typing import Any, Dict, List, Text, Optional, Type
from rasa.nlu.constants import ENTITIES
from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.extractors.extractor import EntityExtractor
from rasa.nlu.training_data import Message

recognizers = {
    'number': recognize_number,
    'ordinal': recognize_ordinal,
    'age': recognize_age,
    'currency': recognize_currency,
    'dimension': recognize_dimension,
    'temperature': recognize_temperature,
    'datetime': recognize_datetime,
    'phone_number': recognize_phone_number,
    'email': recognize_email
}

cultures = {
    'zh': Culture.Chinese,
    'nl': Culture.Dutch,
    'en': Culture.English,
    'fr': Culture.French,
    'it': Culture.Italian,
    'jp': Culture.Japanese,
    'ko': Culture.Korean,
    'pt_br': Culture.Portuguese,
    'es': Culture.Spanish,
    'tr': Culture.Turkish
}


def rasa_format(entity):
    return {
        'entity': entity.type_name,
        'start': entity.start,
        'end': entity.end + 1,
        'value': entity.text
    }


class MicrosoftRecognizersExtractor(EntityExtractor):
    defaults = {
        "dimensions": None,
    }

    def __init__(
            self,
            component_config: Optional[Dict[Text, Any]] = None,
    ) -> None:
        super(MicrosoftRecognizersExtractor, self).__init__(component_config)
        self.language = self.component_config["language"]

    @classmethod
    def create(
            cls, component_config: Dict[Text, Any], config: RasaNLUModelConfig
    ) -> "MicrosoftRecognizersExtractor":
        return cls(component_config)

    def process(self, message: Message, **kwargs: Any) -> None:
        dimensions = self.component_config["dimensions"]
        extracted = self.add_extractor_name(self.extract_entities(message.text, self.language, dimensions))
        message.set(ENTITIES, message.get(ENTITIES, []) + extracted, add_to_output=True)

    @staticmethod
    def extract_entities(user_input: str, language: str, selected_dimensions):
        entities_group = []
        for dimension in recognizers:
            if dimension in selected_dimensions:
                entities = recognizers[dimension](user_input, cultures.get(language, Culture.English))
                if entities:
                    for entity in entities:
                        entities_group.append(rasa_format(entity))

        return entities_group
