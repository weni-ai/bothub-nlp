from typing import List, Type
from rasa.nlu.components import Component
from rasa.nlu.tokenizers.lm_tokenizer import LanguageModelTokenizer


class LanguageModelTokenizerCustom(LanguageModelTokenizer):
    """Tokenizer using transformer based language models.
    Uses the output of HFTransformersNLP component to set the tokens
    for dense featurizable attributes of each message object.
    """

    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        return []
