from rasa.nlu import components
from tempfile import mkdtemp

from bothub.utils.persistor import BothubPersistor
from bothub.utils.backend import backend
from bothub.utils.rasa_components.custom_interpreter import CustomInterpreter


class InterpreterManager:
    interpreters = {}

    def get_interpreter(
        self, repository_version, repository_authorization, rasa_version, use_cache=True
    ):

        update_request = backend().request_backend_parse_nlu_persistor(
            repository_version, repository_authorization, rasa_version, no_bot_data=True
        )

        repository_name = (
            f"{update_request.get('version_id')}_"
            f"{update_request.get('language')}"
        )
        last_training = f"{update_request.get('total_training_end')}"

        # try to fetch cache
        cached_retrieved = self.interpreters.get(repository_name)
        if cached_retrieved and use_cache:
            # return cache only if it's the same training
            if cached_retrieved["last_training"] == last_training:
                return cached_retrieved["interpreter_data"]

        persistor = BothubPersistor(
            repository_version, repository_authorization, rasa_version
        )
        model_directory = mkdtemp()
        persistor.retrieve(str(update_request.get("repository_uuid")), model_directory)

        interpreter = CustomInterpreter(
            None, {"language": update_request.get("language")}
        )
        interpreter = interpreter.load(
            model_directory, components.ComponentBuilder(use_cache=False)
        )

        # update/creates cache
        if use_cache:
            self.interpreters[repository_name] = {
                "last_training": last_training,
                "interpreter_data": interpreter
            }

        return interpreter

    def parse_interpreter(
        self, text, repository_version, repository_authorization, rasa_version, use_cache
    ):
        interpreter = self.get_interpreter(
            repository_version, repository_authorization, rasa_version, use_cache
        )
        return interpreter.parse(text)