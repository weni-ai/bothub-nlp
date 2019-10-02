import os

from rasa_nlu import utils
from rasa_nlu.featurizers.regex_featurizer import RegexFeaturizer as RasaRegexFeaturizer
from rasa_nlu.featurizers.regex_featurizer import REGEX_FEATURIZER_FILE_NAME


class RegexFeaturizer(RasaRegexFeaturizer):
    name = "intent_entity_featurizer_regex"

    @classmethod
    def load(cls, model_dir=None, model_metadata=None, cached_component=None, **kwargs):
        meta = model_metadata.for_component(cls.name)
        file_name = meta.get("regex_file", REGEX_FEATURIZER_FILE_NAME)
        regex_file = os.path.join(model_dir, file_name)

        if os.path.exists(regex_file):
            known_patterns = utils.read_json_file(regex_file)
            return cls(meta, known_patterns=known_patterns)
        else:
            return cls(meta)

    def train(self, training_data, config, **kwargs):
        self.known_patterns = training_data.regex_features
        for example in training_data.training_examples:
            updated = self._text_features_with_regex(example)
            example.set("text_features", updated)
        if training_data.label_training_examples:
            for example in training_data.label_training_examples:
                updated = self._text_features_with_regex(example)
                example.set("text_features", updated)
