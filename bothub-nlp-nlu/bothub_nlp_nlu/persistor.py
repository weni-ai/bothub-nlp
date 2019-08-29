import base64
from tempfile import NamedTemporaryFile

from rasa_nlu.persistor import Persistor
from .utils import backend


class BothubPersistor(Persistor):
    def __init__(self, update=None, repository_authorization=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update = update
        self.repository_authorization = repository_authorization

    def _persist_tar(self, filekey, tarname):
        with open(tarname, 'rb') as tar_file:
            data = tar_file.read()
            backend().send_training_backend_nlu_persistor(self.update, data, self.repository_authorization)

    def retrieve(self, model_name, project, target_path):
        print(self.repository_authorization)
        tar_name = self._tar_name(model_name, project)
        
        tar_data = base64.b64decode(
            backend().request_backend_parse_nlu_persistor(self.update, self.repository_authorization).get('bot_data')
        )
        tar_file = NamedTemporaryFile(suffix=tar_name, delete=False)
        tar_file.write(tar_data)
        tar_file.close()

        self._decompress(tar_file.name, target_path)
