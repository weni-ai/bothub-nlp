import json
from tempfile import mkdtemp
from collections import defaultdict

from rasa.nlu.model import Trainer
from rasa.nlu.training_data import Message, TrainingData
from rasa.nlu.components import ComponentBuilder
from rasa.nlu.training_data.formats.readerwriter import TrainingDataWriter
from rasa.nlu.utils import json_to_string

from .utils import get_rasa_nlu_config_from_update
from .utils import PokeLogging
from .utils import backend
from .utils import get_examples_request
from .utils import get_examples_label_request
from .persistor import BothubPersistor
from . import logger


class BothubWriter(TrainingDataWriter):
    def dumps(self, training_data, **kwargs):  # pragma: no cover
        js_entity_synonyms = defaultdict(list)
        for k, v in training_data.entity_synonyms.items():
            if k != v:
                js_entity_synonyms[v].append(k)

        formatted_synonyms = [
            {"value": value, "synonyms": syns}
            for value, syns in js_entity_synonyms.items()
        ]

        formatted_examples = [
            example.as_dict() for example in training_data.training_examples
        ]

        return json_to_string(
            {
                "rasa_nlu_data": {
                    "common_examples": formatted_examples,
                    "regex_features": training_data.regex_features,
                    "entity_synonyms": formatted_synonyms,
                }
            },
            **kwargs,
        )


class BothubTrainingData(TrainingData):
    def __init__(self, label_training_examples=None, **kwargs):  # pragma: no cover
        if label_training_examples:
            self.label_training_examples = self.sanitize_examples(
                label_training_examples
            )
        else:
            self.label_training_examples = []
        super().__init__(**kwargs)

    def as_json(self, **kwargs):
        return BothubWriter().dumps(self)  # pragma: no cover


def train_update(repository_version, by, repository_authorization):  # pragma: no cover
    update_request = backend().request_backend_start_training_nlu(
        repository_version, by, repository_authorization
    )

    examples_list = get_examples_request(repository_version, repository_authorization)
    examples_label_list = get_examples_label_request(
        repository_version, repository_authorization
    )

    with PokeLogging() as pl:
        try:
            examples = []
            label_examples = []

            for example in examples_list:
                examples.append(
                    Message.build(
                        text=example.get("text"),
                        intent=example.get("intent"),
                        entities=example.get("entities"),
                    )
                )

            for label_example in examples_label_list:
                label_examples.append(
                    Message.build(
                        text=label_example.get("text"),
                        entities=label_example.get("entities"),
                    )
                )

            rasa_nlu_config = get_rasa_nlu_config_from_update(update_request)
            trainer = Trainer(rasa_nlu_config, ComponentBuilder(use_cache=False))
            training_data = TrainingData(training_examples=examples)

            trainer.train(training_data)

            persistor = BothubPersistor(repository_version, repository_authorization)
            trainer.persist(
                mkdtemp(),
                persistor=persistor,
                fixed_model_name=f"{update_request.get('repository_version')}_"
                f"{update_request.get('total_training_end')+1}_"
                f"{update_request.get('language')}",
            )
        except Exception as e:
            logger.exception(e)
            backend().request_backend_trainfail_nlu(
                repository_version, repository_authorization
            )
            raise e
        finally:
            backend().request_backend_traininglog_nlu(
                repository_version, pl.getvalue(), repository_authorization
            )
