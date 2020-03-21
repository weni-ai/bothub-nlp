from rasa.nlu.featurizers.count_vectors_featurizer import CountVectorsFeaturizer


class CountVectorsFeaturizerCustom(CountVectorsFeaturizer):
    @staticmethod
    def _get_message_tokens_by_attribute(message, attribute):
        """Get text tokens of an attribute of a message"""

        tokens = message.get(attribute).split()
        return tokens
