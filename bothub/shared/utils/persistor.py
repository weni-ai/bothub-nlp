import base64
import bothub_backend
import argparse
from tempfile import NamedTemporaryFile

import requests
from rasa.nlu.persistor import Persistor
from decouple import config


class BothubPersistor(Persistor):
    def __init__(
        self,
        repository_version=None,
        repository_authorization=None,
        rasa_version=None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.repository_version = repository_version
        self.repository_authorization = repository_authorization
        self.rasa_version = rasa_version

    def backend(self):
        PARSER = argparse.ArgumentParser()

        # Input Arguments
        PARSER.add_argument(
            "--base_url", help="Base URL API Engine.", type=str, default=None
        )

        ARGUMENTS, _ = PARSER.parse_known_args()

        return bothub_backend.get_backend(
            "bothub_backend.bothub.BothubBackend",
            ARGUMENTS.base_url
            if ARGUMENTS.base_url
            else config("BOTHUB_ENGINE_URL", default="https://api.bothub.it"),
        )

    def _persist_tar(self, filekey, tarname):
        with open(tarname, "rb") as tar_file:
            data = tar_file.read()

            print(len(data))

            save_request = self.backend().send_training_backend_nlu_persistor(
                self.repository_version,
                data,
                self.repository_authorization,
                self.rasa_version,
            )

            print(self.backend().__dict__)
            print(save_request)

    def retrieve(self, model_name, target_path):
        tar_name = self._tar_name(model_name)

        train = self.backend().request_backend_parse_nlu_persistor(
            self.repository_version, self.repository_authorization, self.rasa_version
        )

        if train.get("from_aws"):
            tar_data = requests.get(train.get("bot_data")).content
        else:
            tar_data = base64.b64decode(train.get("bot_data"))  # pragma: no cover

        tar_file = NamedTemporaryFile(suffix=tar_name, delete=False)
        tar_file.write(tar_data)
        tar_file.close()

        self._decompress(tar_file.name, target_path)
