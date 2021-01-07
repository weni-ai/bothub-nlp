from tempfile import mkdtemp
import os
import logging
from rasa.nlu import __version__ as rasa_version
from rasa.nlu.model import Trainer
from rasa.nlu.training_data import Message, TrainingData
from rasa.nlu.components import ComponentBuilder

from bothub.shared.utils.poke_logging import PokeLogging
from bothub.shared.utils.backend import backend
from bothub.shared.utils.examples_request import get_examples_request
from bothub.shared.utils.persistor import BothubPersistor
from bothub.shared.utils.pipeline_builder import get_rasa_nlu_config

logger = logging.getLogger(__name__)


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def load_lookup_tables(update_request):
    lookup_tables = []
    language = update_request.get("language")
    supported_lookup_table_entities = ['country', 'cep', 'cpf', 'brand']

    # Try to load lookup_tables
    if update_request.get("prebuilt_entities"):
        # TODO: load lookup tables from backend instead of this (locally)
        runtime_path = os.path.dirname(os.path.abspath(__file__))
        entities = intersection(update_request.get("prebuilt_entities"), supported_lookup_table_entities)
        for entity in entities:
            file_path = os.path.join(runtime_path, 'lookup_tables', language, entity+'.txt')
            # Check if lookup_table exists
            if os.path.exists(file_path):
                lookup_tables.append(
                    {'name': entity, 'elements': file_path},
                )
            else:
                print("Not found lookup_table in path: " + file_path)

    return lookup_tables


def train_update(repository_version, by, repository_authorization, from_queue='celery'):  # pragma: no cover
    update_request = backend().request_backend_start_training_nlu(
        repository_version, by, repository_authorization, from_queue
    )

    """ update_request (v2/repository/preprocessing/authorization/train/start_training/) signature:
    {
        'language': 'pt_br',
        'repository_version': 47,
        'repository_uuid': '1d8e0d6f-1941-42a3-84c5-788706c7072e',
        'intent': [4, 5],
        'algorithm': 'transformer_network_diet_bert',
        'use_name_entities': False,
        'use_competing_intents': False,
        'use_analyze_char': False,
        'total_training_end': 0
    }
    """
    # TODO: update_request must include list of
    #       lookup_tables the user choose to use in webapp

    examples_list = get_examples_request(repository_version, repository_authorization)

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

            update_request['prebuilt_entities'] = ['number', 'ordinal', 'age', 'currency', 'dimension', 'temperature',
                                                   'datetime', 'phone_number', 'email', 'country', 'cep', 'cpf',
                                                   'brand']
            lookup_tables = load_lookup_tables(update_request)
            print("Loaded lookup_tables: " + str(lookup_tables))

            rasa_nlu_config = get_rasa_nlu_config(update_request)
            trainer = Trainer(rasa_nlu_config, ComponentBuilder(use_cache=False))
            training_data = TrainingData(
                training_examples=examples,
                lookup_tables=lookup_tables,
            )

            trainer.train(training_data)

            persistor = BothubPersistor(
                repository_version, repository_authorization, rasa_version
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
                repository_version, repository_authorization
            )
            raise e
        finally:
            backend().request_backend_traininglog_nlu(
                repository_version, pl.getvalue(), repository_authorization
            )
