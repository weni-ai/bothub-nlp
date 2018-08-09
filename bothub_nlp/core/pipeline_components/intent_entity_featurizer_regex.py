from rasa_nlu.featurizers.regex_featurizer import RegexFeaturizer \
    as RasaRegexFeaturizer


class RegexFeaturizer(RasaRegexFeaturizer):
    name = 'bothub_nlp.core.pipeline_components.' \
            'intent_entity_featurizer_regex.RegexFeaturizer'

    def train(self, training_data, config, **kwargs):
        self.known_patterns = training_data.regex_features
        for example in training_data.training_examples:
            updated = self._text_features_with_regex(example)
            example.set('text_features', updated)
        if training_data.label_training_examples:
            for example in training_data.label_training_examples:
                updated = self._text_features_with_regex(example)
                example.set('text_features', updated)
