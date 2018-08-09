from rasa_nlu.extractors.crf_entity_extractor import CRFEntityExtractor


class CRFLabelAsEntityExtractor(CRFEntityExtractor):
    name = 'bothub_nlp.core.pipeline_components.' \
            'crf_label_as_entity_extractor.CRFLabelAsEntityExtractor'

    provides = ['labels_as_entity']

    requires = ['spacy_doc', 'tokens']

    def train(self, training_data, config, **kwargs):
        self.component_config = config.for_component(self.name, self.defaults)
        self._validate_configuration()
        if training_data.entity_examples:
            filtered_entity_examples = self.filter_trainable_entities(
                    training_data.label_training_examples)
            dataset = self._create_dataset(filtered_entity_examples)
            self._train_model(dataset)
