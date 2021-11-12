from bothub.shared.utils.helpers import ALGORITHM_TO_LANGUAGE_MODEL
from bothub_nlp_celery import settings
from bothub.shared.utils.rasa_components.registry import language_to_model
from rasa.nlu.config import RasaNLUModelConfig


class PipelineBuilder:
    def __init__(self, update):
        self.language = update.get("language")
        self.algorithm = update.get("algorithm")
        self.use_name_entities = update.get("use_name_entities")
        self.use_competing_intents = update.get("use_competing_intents")
        self.use_analyze_char = update.get("use_analyze_char")
        self.prebuilt_entities = update.get("prebuilt_entities", [])
        self.model = self._build_model_requirements()
        self.pipeline = self._build_pipeline()

    def _add_spacy_nlp(self):
        return {"name": "bothub.shared.utils.pipeline_components.spacy_nlp.SpacyNLP"}

    def _add_whitespace_tokenizer(self):
        return {"name": "WhitespaceTokenizer"}

    def _add_preprocessing(self):
        return {
            "name": "bothub.shared.utils.pipeline_components.preprocessing.Preprocessing",
            "language": self.language,
        }

    def _add_regex_entity_extractor(self):
        return {
            "name": "bothub.shared.utils.pipeline_components.regex_entity_extractor.RegexEntityExtractorCustom"
        }

    def _add_countvectors_featurizer(self):
        featurizers = []

        if self.use_analyze_char:
            featurizers.append(
                {
                    "name": "CountVectorsFeaturizer",
                    "analyzer": "char_wb",
                    "min_ngram": 3,
                    "max_ngram": 3,
                }
            )

        featurizers.append(
            {"name": "CountVectorsFeaturizer", "token_pattern": r"(?u)\b\w+\b"}
        )

        return featurizers

    def _add_legacy_countvectors_featurizer(self):
        if self.use_analyze_char:
            return {
                "name": "CountVectorsFeaturizer",
                "analyzer": "char_wb",
                "min_ngram": 3,
                "max_ngram": 3,
            }
        else:
            return {"name": "CountVectorsFeaturizer", "token_pattern": r"(?u)\b\w+\b"}

    def _add_microsoft_entity_extractor(self):
        return {
            "name": "bothub.shared.utils.pipeline_components.microsoft_recognizers_extractor.MicrosoftRecognizersExtractor",
            "dimensions": self.prebuilt_entities,
            "language": self.language,
        }

    def _add_embedding_intent_classifier(self):
        return {
            "name": "bothub.shared.utils.pipeline_components.diet_classifier.DIETClassifierCustom",
            "hidden_layers_sizes": {"text": [256, 128]},
            "number_of_transformer_layers": 0,
            "weight_sparsity": 0,
            "intent_classification": True,
            "entity_recognition": True,
            "use_masked_language_model": False,
            "BILOU_flag": False,
        }

    def _add_diet_classifier(self, epochs=300, bert=False):
        model = {
            "name": "bothub.shared.utils.pipeline_components.diet_classifier.DIETClassifierCustom",
            "entity_recognition": True,
            "BILOU_flag": False,
            "epochs": epochs,
        }

        if bert:
            model["hidden_layer_sizes"] = {"text": [256, 64]}

        return model

    def _legacy_internal_config(self):
        partial_pipeline = [
            self._add_whitespace_tokenizer(),  # Tokenizer
            self._add_legacy_countvectors_featurizer(),  # Featurizer
            self._add_embedding_intent_classifier(),  # Intent Classifier
        ]
        return partial_pipeline

    def _legacy_external_config(self):
        partial_pipeline = [
            {"name": "SpacyTokenizer"},  # Tokenizer
            {"name": "SpacyFeaturizer"},  # Spacy Featurizer
            self._add_legacy_countvectors_featurizer(),  # Bag of Words Featurizer
            self._add_embedding_intent_classifier(),  # intent classifier
        ]
        return partial_pipeline

    def _transformer_network_diet_config(self):
        partial_pipeline = [self._add_whitespace_tokenizer()]

        # partial_pipeline.append(add_regex_entity_extractor())
        # if self.prebuilt_entities:
        #     partial_pipeline.append(add_microsoft_entity_extractor(update))  # Microsoft Entity Extractor)
        partial_pipeline.extend(
            self._add_countvectors_featurizer()
        )  # Bag of Words Featurizer
        partial_pipeline.append(
            self._add_diet_classifier(epochs=150)
        )  # Intent Classifier

        return partial_pipeline

    def _transformer_network_diet_word_embedding_config(self):
        partial_pipeline = [
            {"name": "SpacyTokenizer"},  # Tokenizer
            {"name": "SpacyFeaturizer"},  # Spacy Featurizer
        ]
        partial_pipeline.extend(
            self._add_countvectors_featurizer()
        )  # Bag of Words Featurizer
        partial_pipeline.append(
            self._add_diet_classifier(epochs=200)
        )  # Intent Classifier

        return partial_pipeline

    def _transformer_network_diet_bert_config(self):
        partial_pipeline = [
            {  # NLP
                "name": "bothub.shared.utils.pipeline_components.hf_transformer.HFTransformersNLPCustom",
                "model_name": language_to_model.get(self.language, "bert_multilang"),
            },
            {  # Tokenizer
                "name": "bothub.shared.utils.pipeline_components.lm_tokenizer.LanguageModelTokenizerCustom",
                "intent_tokenization_flag": False,
                "intent_split_symbol": "_",
            },
            {  # Bert Featurizer
                "name": "bothub.shared.utils.pipeline_components.lm_featurizer.LanguageModelFeaturizerCustom"
            },
        ]
        # partial_pipeline.append(add_regex_entity_extractor())
        # if self.prebuilt_entities:
        #     partial_pipeline.append(add_microsoft_entity_extractor(update))  # Microsoft Entity Extractor)

        partial_pipeline.extend(
            self._add_countvectors_featurizer()
        )  # Bag of Words Featurizers
        partial_pipeline.append(
            self._add_diet_classifier(epochs=100, bert=True)
        )  # Intent Classifier

        return partial_pipeline

    def _build_model_requirements(self):
        model = ALGORITHM_TO_LANGUAGE_MODEL[self.algorithm]
        if model == "SPACY" and self.language not in settings.AVAILABLE_SPACY_MODELS:
            model = None
            if self.algorithm == "neural_network_external":
                self.algorithm = "neural_network_internal"
            else:
                self.algorithm = "transformer_network_diet"

        return model

    def _build_pipeline(self):
        pipeline = [self._add_preprocessing()]

        if (
            self.use_name_entities
            and self.algorithm != "transformer_network_diet_bert"
            and self.language in settings.AVAILABLE_SPACY_MODELS
        ) or self.algorithm in [
            "neural_network_external",
            "transformer_network_diet_word_embedding",
        ]:
            pipeline.append(self._add_spacy_nlp())

        if self.algorithm == "neural_network_internal":
            pipeline.extend(self._legacy_internal_config())
        elif self.algorithm == "neural_network_external":
            pipeline.extend(self._legacy_external_config())
        elif self.algorithm == "transformer_network_diet_bert":
            pipeline.extend(self._transformer_network_diet_bert_config())
        elif self.algorithm == "transformer_network_diet_word_embedding":
            pipeline.extend(self._transformer_network_diet_word_embedding_config())
        else:
            pipeline.extend(self._transformer_network_diet_config())

        if (
            self.use_name_entities
            and self.algorithm != "transformer_network_diet_bert"
            and self.language in settings.AVAILABLE_SPACY_MODELS
        ):
            pipeline.append({"name": "SpacyEntityExtractor"})

        return pipeline

    def print_pipeline(self):
        import json

        print(f"Pipeline Config:")
        for component in self.pipeline:
            print(json.dumps(component, indent=2))

    def get_nlu_model(self):
        return RasaNLUModelConfig(
            {"language": self.language, "pipeline": self.pipeline}
        )
