from rasa.nlu.config import RasaNLUModelConfig
from bothub_nlp_celery.utils import ALGORITHM_TO_LANGUAGE_MODEL
from bothub_nlp_celery import settings
from bothub.shared.utils.rasa_components.registry import language_to_model


def add_spacy_nlp():
    return {"name": "bothub.shared.utils.pipeline_components.spacy_nlp.SpacyNLP"}


def add_whitespace_tokenizer():
    return {"name": "WhitespaceTokenizer"}


def add_preprocessing(update):
    return {
        "name": "bothub.shared.utils.pipeline_components.preprocessing.Preprocessing",
        "language": update.get("language"),
    }


def add_regex_featurizer():
    return {
        "name": "bothub.shared.utils.pipeline_components.regex_featurizer.RegexFeaturizerCustom",
        "case_sensitive": False
    }


def add_regex_entity_extractor():
    return {
        "name": "bothub.shared.utils.pipeline_components.regex_entity_extractor.RegexEntityExtractorCustom",
    }


def add_countvectors_featurizer(update):
    featurizers = []

    if update.get("use_analyze_char"):
        featurizers.append(
            {
                "name": "CountVectorsFeaturizer",
                "analyzer": "char_wb",
                "min_ngram": 3,
                "max_ngram": 3
            }
        )

    featurizers.append(
        {
            "name": "CountVectorsFeaturizer",
            "token_pattern": r'(?u)\b\w+\b'
        }
    )

    return featurizers


def add_legacy_countvectors_featurizer(update):
    if update.get("use_analyze_char"):
        return {
            "name": "CountVectorsFeaturizer",
            "analyzer": "char_wb",
            "min_ngram": 3,
            "max_ngram": 3
        }
    else:
        return {
            "name": "CountVectorsFeaturizer",
            "token_pattern": r'(?u)\b\w+\b'
        }


def add_microsoft_entity_extractor(update):
    return {
        "name": "bothub.shared.utils.pipeline_components.microsoft_recognizers_extractor.MicrosoftRecognizersExtractor",
        "dimensions": update['prebuilt_entities'],
        "language": update.get('language')
    }


def add_embedding_intent_classifier():
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


def add_diet_classifier(epochs=300, bert=False):
    model = {
        "name": "bothub.shared.utils.pipeline_components.diet_classifier.DIETClassifierCustom",
        "entity_recognition": True,
        "BILOU_flag": False,
        "epochs": epochs
    }

    if bert:
        model["hidden_layer_sizes"] = {"text": [256, 64]}

    return model


def legacy_internal_config(update):
    pipeline = [
        add_whitespace_tokenizer(),  # Tokenizer
        add_legacy_countvectors_featurizer(update),  # Featurizer
        add_embedding_intent_classifier(),  # Intent Classifier
    ]
    return pipeline


def legacy_external_config(update):
    pipeline = [
        {"name": "SpacyTokenizer"},  # Tokenizer
        {"name": "SpacyFeaturizer"},  # Spacy Featurizer
        add_legacy_countvectors_featurizer(update),  # Bag of Words Featurizer
        add_embedding_intent_classifier(),  # intent classifier
    ]
    return pipeline


def transformer_network_diet_config(update):
    pipeline = [add_whitespace_tokenizer()]

    # pipeline.append(add_regex_entity_extractor())
    # if update.get('prebuilt_entities'):
    #     pipeline.append(add_microsoft_entity_extractor(update))  # Microsoft Entity Extractor)
    pipeline.extend(add_countvectors_featurizer(update))  # Bag of Words Featurizer
    pipeline.append(add_diet_classifier(epochs=150))  # Intent Classifier

    return pipeline


def transformer_network_diet_word_embedding_config(update):
    pipeline = [
        {"name": "SpacyTokenizer"},  # Tokenizer
        {"name": "SpacyFeaturizer"},  # Spacy Featurizer
    ]
    pipeline.extend(add_countvectors_featurizer(update))  # Bag of Words Featurizer
    pipeline.append(add_diet_classifier(epochs=200))  # Intent Classifier

    return pipeline


def transformer_network_diet_bert_config(update):
    pipeline = [
        {  # NLP
            "name": "bothub.shared.utils.pipeline_components.hf_transformer.HFTransformersNLPCustom",
            "model_name": language_to_model.get(update.get("language"), 'bert_multilang'),
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
    # pipeline.append(add_regex_entity_extractor())
    # if update.get('prebuilt_entities'):
    #     pipeline.append(add_microsoft_entity_extractor(update))  # Microsoft Entity Extractor)

    pipeline.extend(add_countvectors_featurizer(update))  # Bag of Words Featurizers
    pipeline.append(add_diet_classifier(epochs=100, bert=True))  # Intent Classifier

    return pipeline


def get_rasa_nlu_config(update):
    pipeline = []

    # algorithm = choose_best_algorithm(update.get("language"))
    algorithm = update.get('algorithm')
    language = update.get('language')

    model = ALGORITHM_TO_LANGUAGE_MODEL[algorithm]
    if model == 'SPACY' and language not in settings.SPACY_LANGUAGES:
        if algorithm == 'neural_network_external':
            algorithm = "neural_network_internal"
        else:
            algorithm = "transformer_network_diet"

    pipeline.append(add_preprocessing(update))

    if (update.get(
            "use_name_entities") and algorithm != 'transformer_network_diet_bert' and language in settings.SPACY_LANGUAGES) or algorithm in [
        'neural_network_external', 'transformer_network_diet_word_embedding']:
        pipeline.append(add_spacy_nlp())

    if algorithm == "neural_network_internal":
        pipeline.extend(legacy_internal_config(update))
    elif algorithm == "neural_network_external":
        pipeline.extend(legacy_external_config(update))
    elif algorithm == "transformer_network_diet_bert":
        pipeline.extend(transformer_network_diet_bert_config(update))
    elif algorithm == "transformer_network_diet_word_embedding":
        pipeline.extend(transformer_network_diet_word_embedding_config(update))
    else:
        pipeline.extend(transformer_network_diet_config(update))

    if update.get(
            "use_name_entities") and algorithm != 'transformer_network_diet_bert' and language in settings.SPACY_LANGUAGES:
        pipeline.append({"name": "SpacyEntityExtractor"})

    import json
    print(f"New pipeline:")
    for component in pipeline:
        print(json.dumps(component, indent=2))

    return RasaNLUModelConfig(
        {
            "language": update.get("language"),
            "pipeline": pipeline
        }
    )
