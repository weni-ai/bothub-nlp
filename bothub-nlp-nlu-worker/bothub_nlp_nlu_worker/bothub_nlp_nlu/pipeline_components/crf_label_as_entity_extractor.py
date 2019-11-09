import os

from rasa.nlu.extractors.crf_entity_extractor import CRFEntityExtractor


CRF_MODEL_FILE_NAME = "crf_model_labels.pkl"


class CRFLabelAsEntityExtractor(CRFEntityExtractor):
    name = "crf_label_as_entity_extractor"

    provides = ["labels_as_entity"]

    @classmethod
    def load(
        cls, meta, model_dir=None, model_metadata=None, cached_component=None, **kwargs
    ):
        from sklearn.externals import joblib

        file_name = meta.get("classifier_file", CRF_MODEL_FILE_NAME)
        model_file = os.path.join(model_dir, file_name)
        if os.path.exists(model_file):
            ent_tagger = joblib.load(model_file)
            return cls(meta, ent_tagger)
        else:
            return cls(meta)

    def train(self, training_data, config, **kwargs):
        if training_data.label_training_examples:
            self._check_spacy_doc(training_data.training_examples[0])
            filtered_entity_examples = self.filter_trainable_entities(
                training_data.label_training_examples
            )
            dataset = self._create_dataset(filtered_entity_examples)
            self._train_model(dataset)

    def persist(self, file_name, model_dir):
        from sklearn.externals import joblib

        if self.ent_tagger:
            model_file_name = os.path.join(model_dir, CRF_MODEL_FILE_NAME)
            joblib.dump(self.ent_tagger, model_file_name)
        return {"classifier_file": CRF_MODEL_FILE_NAME}

    def process(self, message, **kwargs):
        extracted = self.add_extractor_name(self.extract_entities(message))
        message.set(
            "labels_as_entity",
            message.get("labels_as_entity", []) + extracted,
            add_to_output=True,
        )

    def _create_entity_dict(self, message, tokens, start, end, entity, confidence):
        d = super()._create_entity_dict(message, tokens, start, end, entity, confidence)
        d.update({"label_as_entity": True})
        return d
