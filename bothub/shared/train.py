from tempfile import mkdtemp
import os
import logging
from rasa.nlu import __version__ as rasa_version
from rasa.nlu.model import Trainer
from rasa.nlu.training_data import Message, TrainingData
from rasa.nlu.components import ComponentBuilder

from bothub.shared.utils.poke_logging import PokeLogging
from bothub.shared.utils.backend import backend
from bothub.shared.utils.helpers import get_examples_request
from bothub.shared.utils.persistor import BothubPersistor
from bothub.shared.utils.pipeline_builder import PipelineBuilder

logger = logging.getLogger(__name__)


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def train_update(
    repository_version_language_id, by_user, repository_authorization, from_queue="celery"
):  # pragma: no cover

    update_request = backend().request_backend_start_training_nlu(
        repository_version_language_id, by_user, repository_authorization, from_queue
    )

    examples_list = get_examples_request(repository_version_language_id, repository_authorization)

    with PokeLogging() as pl:
        try:
            examples = []

            for example in examples_list:
                examples.append(
                    Message.build(
                        text=example.get("text"),
                        intent=example.get("intent"),
                        entities=example.get("entities"),
                    )
                )

            update_request["dataset_size"] = len(examples)

            pipeline_builder = PipelineBuilder(update_request)
            pipeline_builder.print_pipeline()
            rasa_nlu_config = pipeline_builder.get_nlu_model()

            trainer = Trainer(rasa_nlu_config, ComponentBuilder(use_cache=False))
            training_data = TrainingData(
                training_examples=examples, lookup_tables=None
            )

            trainer.train(training_data)

            persistor = BothubPersistor(
                repository_version_language_id, repository_authorization, rasa_version
            )
            trainer.persist(
                mkdtemp(),
                persistor=persistor,
                fixed_model_name=f"{update_request.get('repository_version')}_"
                f"{update_request.get('total_training_end') + 1}_"
                f"{update_request.get('language')}",
            )
        except Exception as e:
            logger.exception(e)
            backend().request_backend_trainfail_nlu(
                repository_version_language_id, repository_authorization
            )
            raise e
        finally:
            backend().request_backend_traininglog_nlu(
                repository_version_language_id, pl.getvalue(), repository_authorization
            )
