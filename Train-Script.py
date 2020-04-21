import json

import bothub_backend


class Core:
    def __init__(self):
        self.SUPPORTED_LANGUAGES = ["pt_br"]
        self.TRAIN_STATUS_TRAINED = "trained"
        self.TRAIN_STATUS_FAILED = "failed"
        self.TRAIN_STATUS_NOT_READY_FOR_TRAIN = "not_ready_for_train"

    def get_repository_authorization(self, authorization_header_value):
        authorization_uuid = authorization_header_value and authorization_header_value[7:]

        if not authorization_uuid:
            return False

        return authorization_uuid

    def backend(self):
        return bothub_backend.get_backend(
            "bothub_backend.bothub.BothubBackend", "http://localhost:8000"
        )

    def get_examples_request(self, update_id, repository_authorization):  # pragma: no cover
        start_examples = self.backend().request_backend_get_examples(
            update_id, False, None, repository_authorization
        )

        examples = start_examples.get("results")

        page = start_examples.get("next")

        if page:
            while True:
                request_examples_page = self.backend().request_backend_get_examples(
                    update_id, True, page, repository_authorization
                )

                examples += request_examples_page.get("results")

                if request_examples_page.get("next") is None:
                    break

                page = request_examples_page.get("next")

        return examples

    def get_examples_label_request(self, update_id, repository_authorization):  # pragma: no cover
        start_examples = self.backend().request_backend_get_examples_labels(
            update_id, False, None, repository_authorization
        )

        examples_label = start_examples.get("results")

        page = start_examples.get("next")

        if page:
            while True:
                request_examples_page = self.backend().request_backend_get_examples_labels(
                    update_id, True, page, repository_authorization
                )

                examples_label += request_examples_page.get("results")

                if request_examples_page.get("next") is None:
                    break

                page = request_examples_page.get("next")

        return examples_label

    def get_rasa_nlu_config_from_update(self, update):  # pragma: no cover
        pipeline = []
        use_spacy = update.get("algorithm") == update.get(
            "ALGORITHM_NEURAL_NETWORK_EXTERNAL"
        )
        # load spacy
        pipeline.append(
            {
                "name": "bothub_nlp_nlu.pipeline_components."
                        "optimized_spacy_nlp_with_labels.SpacyNLP"
            }
        )
        # tokenizer
        pipeline.append(
            {
                "name": "bothub_nlp_nlu.pipeline_components."
                        "tokenizer_spacy_with_labels.SpacyTokenizer"
            }
        )
        # featurizer
        if use_spacy:
            pipeline.append({"name": "SpacyFeaturizer"})
        else:
            if update.get("use_analyze_char"):
                pipeline.append(
                    {
                        "name": "CountVectorsFeaturizer",
                        "analyzer": "char",
                        "min_ngram": 3,
                        "max_ngram": 3,
                        "token_pattern": "(?u)\\b\\w+\\b",
                    }
                )
            else:
                pipeline.append(
                    {
                        "name": "bothub_nlp_nlu.pipeline_components."
                                "count_vectors_featurizer_no_lemmatize.CountVectorsFeaturizerCustom",
                        "token_pattern": "(?u)\\b\\w+\\b",
                    }
                )
        # intent classifier
        pipeline.append(
            {
                "name": "EmbeddingIntentClassifier",
                "similarity_type": "inner"
                if update.get("use_competing_intents")
                else "cosine",
            }
        )

        # entity extractor
        pipeline.append({"name": "CRFEntityExtractor"})
        # spacy named entity recognition
        if update.get("use_name_entities"):
            pipeline.append({"name": "SpacyEntityExtractor"})
        # label extractor
        pipeline.append(
            {
                "name": "bothub_nlp_nlu.pipeline_components."
                        "crf_label_as_entity_extractor.CRFLabelAsEntityExtractor"
            }
        )
        return {"language": update.get("language"), "pipeline": pipeline}

    def train_handler(self, authorization, repository_version=None):
        repository_authorization = self.get_repository_authorization(authorization)

        languages_report = {}

        for language in self.SUPPORTED_LANGUAGES:

            current_update = self.backend().request_backend_train(
                repository_authorization, language, repository_version
            )
            print(current_update)

            if not current_update.get("ready_for_train"):
                languages_report[language] = {"status": self.TRAIN_STATUS_NOT_READY_FOR_TRAIN}
                continue

            self.train_update(
                current_update.get("current_version_id"),
                current_update.get("repository_authorization_user_id"),
                repository_authorization
            )


        resp = {
            "SUPPORTED_LANGUAGES": list(self.SUPPORTED_LANGUAGES),
            "languages_report": languages_report,
        }
        return resp

    def train_update(self, repository_version, by, repository_authorization):  # pragma: no cover
        update_request = self.backend().request_backend_start_training_nlu(
            repository_version, by, repository_authorization
        )

        examples_list = self.get_examples_request(repository_version, repository_authorization)
        examples_label_list = self.get_examples_label_request(
            repository_version, repository_authorization
        )

        examples = []
        label_examples = []

        print(examples_list)

        get_examples = self.backend().request_backend_get_entities_and_labels_nlu(
            repository_version,
            update_request.get("language"),
            json.dumps(
                {
                    "examples": examples_list,
                    "label_examples_query": examples_label_list,
                    "repository_version": repository_version,
                }
            ),
            repository_authorization,
        )

        for example in get_examples.get("examples"):
            examples.append(
                {
                    "text": example.get("text"),
                    "intent": example.get("intent"),
                    "entities": example.get("entities"),
                }
            )

        for label_example in get_examples.get("label_examples"):
            label_examples.append(
                {
                    "text": label_example.get("text"),
                    "entities": label_example.get("entities"),
                }
            )

        rasa_nlu_config = self.get_rasa_nlu_config_from_update(update_request)
        print(f"rasa_nlu_config: {rasa_nlu_config}")
        print(f"training_examples: {examples}")
        print(f"label_training_examples: {label_examples}")
        print(f"fixed_model_name={update_request.get('repository_version')}_{update_request.get('total_training_end') + 1}_{update_request.get('language')}")


train_handler = Core().train_handler("Bearer 90acbc75-3385-4238-bd54-69e724462e71", 2)
