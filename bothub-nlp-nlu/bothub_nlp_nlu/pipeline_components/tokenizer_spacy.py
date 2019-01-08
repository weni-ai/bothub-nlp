from rasa_nlu.tokenizers.spacy_tokenizer import SpacyTokenizer \
    as RasaSpacyTokenizer


class SpacyTokenizer(RasaSpacyTokenizer):
    name = 'bothub_nlp_nlu.pipeline_components.tokenizer_spacy.' \
            'SpacyTokenizer'

    def train(self, training_data, config, **kwargs):
        for example in training_data.training_examples:
            example.set('tokens', self.tokenize(example.get('spacy_doc')))
        if training_data.label_training_examples:
            for example in training_data.label_training_examples:
                example.set('tokens', self.tokenize(example.get('spacy_doc')))
