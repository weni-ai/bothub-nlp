from typing import List, Callable

from bothub.shared.utils.helpers import ALGORITHM_TO_LANGUAGE_MODEL
from bothub_nlp_celery import settings
from bothub.shared.utils.rasa_components.registry import language_to_model
from rasa.nlu.config import RasaNLUModelConfig


class PipelineBuilder:
    def __init__(self, update):
        self.language = update.get("language")
        self.algorithm = update.get("algorithm")
        self.use_name_entities = update.get("use_name_entities")
        self.dataset_size = update.get("dataset_size")
        self.use_competing_intents = update.get("use_competing_intents")
        self.use_analyze_char = update.get("use_analyze_char")
        self.prebuilt_entities = update.get("prebuilt_entities", [])
        self.model = self._build_model_requirements()
        self.pipeline = self._build_pipeline()

    @staticmethod
    def _add_spacy_nlp():
        return {"name": "bothub.shared.utils.pipeline_components.spacy_nlp.SpacyNLP"}

    @staticmethod
    def _add_whitespace_tokenizer():
        return {"name": "WhitespaceTokenizer"}

    def _add_preprocessing(self):
        return {
            "name": "bothub.shared.utils.pipeline_components.preprocessing.Preprocessing",
            "language": self.language,
        }

    @staticmethod
    def _add_regex_entity_extractor():
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

    @staticmethod
    def _add_embedding_intent_classifier():
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

    @staticmethod
    def _epoch_factor_function1(examples_qnt: int, min_threshold: int = 10000) -> float:
        """
        :param examples_qnt: Number of examples in dataset
        :param min_threshold: Minimum number of examples needed to have a factor > 1
        :return: Division factor of defined maximum epochs

        Example:
        min_threshold = 10000
          examples_qnt = 10000  -> (10*(10000-10000) + 100*10000)//10000   = 100 -> 100/100 = 1.0 (base case)
          examples_qnt = 11000  -> (10*(11000-10000) + 100*10000)//11000   =  91 -> 100/91  = 1.09
          examples_qnt = 15000  -> (10*(15000-10000) + 100*10000)//15000   =  70 -> 100/70  = 1,42
          examples_qnt = 30000  -> (10*(30000-10000) + 100*10000)//30000   =  40 -> 100/40  = 2,5
          examples_qnt = 33000  -> (10*(33000-10000) + 100*10000)//33000   =  37 -> 100/37  = 2,7
          examples_qnt = 50000  -> (10*(50000-10000) + 100*10000)//50000   =  28 -> 100/28  = 3,57
          examples_qnt = 100000 -> (10*(100000-10000) + 100*10000)//100000 =  19 -> 100/19  = 5,26

        min_threshold = 5000
          examples_qnt = 5000  -> (10*(5000-5000) + 100*5000)//5000   = 100 -> 100/100 = 1.0 (base case)
          examples_qnt = 10000 -> (10*(10000-5000) + 100*5000)//10000 = 55  -> 100/55  = 1.81
          examples_qnt = 15000 -> (10*(15000-5000) + 100*5000)//15000 = 40  -> 100/40  = 2,5

        """
        if examples_qnt <= min_threshold:
            return 1.0

        over_qnt = examples_qnt - min_threshold
        epochs_fraction = ((10*over_qnt) + (100*min_threshold)) // examples_qnt
        factor = 100 / epochs_fraction

        return factor

    def _calculate_epochs_number(
        self,
        max_epochs: int,
        factor_function: Callable[[int, int], float]
    ) -> int:
        """
        :param max_epochs: Maximum number of epochs to be considered
        :param factor_function: Function that returns the division factor
        :return: Calculated number of epochs (max_epochs/calculated_factor)
        """
        min_threshold = 10000

        if self.dataset_size < min_threshold:
            return max_epochs

        factor = factor_function(self.dataset_size, min_threshold)
        epochs = int(max_epochs // factor)
        return epochs

    def _add_diet_classifier(self, max_epochs=300, bert=False):
        epochs = self._calculate_epochs_number(max_epochs, self._epoch_factor_function1)

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
            self._add_diet_classifier(max_epochs=150)
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
            self._add_diet_classifier(max_epochs=200)
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
            self._add_diet_classifier(max_epochs=100, bert=True)
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
