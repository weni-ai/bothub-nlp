from rasa.nlu.featurizers.dense_featurizer.lm_featurizer import LanguageModelFeaturizer
from typing import List, Type
from rasa.nlu.components import Component


class LanguageModelFeaturizerCustom(LanguageModelFeaturizer):

    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        return []
