import logging
import threading
import time
import gc

from typing import Callable, Union
from rasa.nlu import components
from tempfile import mkdtemp
from datetime import datetime

from bothub import settings
from bothub.shared.utils.persistor import BothubPersistor
from bothub.shared.utils.backend import backend
from bothub.shared.utils.rasa_components.bothub_interpreter import BothubInterpreter

logger = logging.getLogger(__name__)


class SetInterval:
    """
    Creates a thread that execute a function every x seconds
    """
    def __init__(self, interval: Union[int, float], action: Callable):
        """
        :param interval: Period in seconds
        :param action: Callable function
        """
        self.interval = interval
        self.action = action
        self.stopEvent = threading.Event()
        thread = threading.Thread(target=self._set_interval, daemon=True)
        thread.start()

    def _set_interval(self):
        next_time = time.time() + self.interval
        while not self.stopEvent.wait(next_time - time.time()):
            next_time += self.interval
            self.action()

    def cancel(self):
        self.stopEvent.set()


class InterpreterManager:
    def __init__(self):
        self.cached_interpreters = {}
        SetInterval(settings.WORKER_CACHE_CLEANING_PERIOD, self._clean_cache)

    def get_interpreter(
        self,
        repository_version,
        repository_authorization,
        rasa_version,
        use_cache=True
    ) -> BothubInterpreter:

        update_request = backend().request_backend_parse_nlu_persistor(
            repository_version, repository_authorization, rasa_version, no_bot_data=True
        )

        repository_name = (
            f"{update_request.get('version_id')}_" f"{update_request.get('language')}"
        )
        last_training = f"{update_request.get('total_training_end')}"

        # tries to fetch cache
        retrieved_cache = self.cached_interpreters.get(repository_name)
        if retrieved_cache and use_cache:
            # retrieve cache only if it's the same training
            if retrieved_cache["last_training"] == last_training:
                retrieved_cache["last_request"] = datetime.now()
                return retrieved_cache["interpreter_data"]

        persistor = BothubPersistor(
            repository_version, repository_authorization, rasa_version
        )
        model_directory = mkdtemp()
        persistor.retrieve(str(update_request.get("repository_uuid")), model_directory)

        interpreter = BothubInterpreter(
            None, {"language": update_request.get("language")}
        )
        interpreter = interpreter.load(
            model_directory, components.ComponentBuilder(use_cache=False)
        )

        if use_cache:  # update/creates cache
            self.cached_interpreters[repository_name] = {
                "last_training": last_training,
                "interpreter_data": interpreter,
                "last_request": datetime.now()
            }

        return interpreter

    def _clean_cache(self) -> None:
        logger.info("Cleaning repositories cache")
        cur_time = datetime.now()

        to_remove = []
        for interpreter in self.cached_interpreters:
            idle_time = (cur_time - self.cached_interpreters[interpreter]['last_request']).total_seconds()
            if idle_time > settings.INTERPRETER_CACHE_IDLE_LIMIT:
                to_remove.append(interpreter)

        for interpreter in to_remove:
            del self.cached_interpreters[interpreter]

        objects_collected = gc.collect()
        logger.info(f"{objects_collected} objects collected")
