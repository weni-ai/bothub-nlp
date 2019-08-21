import base64
import requests
from tempfile import NamedTemporaryFile

from rasa_nlu.persistor import Persistor


class BothubPersistor(Persistor):
    def __init__(self, update=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update = update

    def _persist_tar(self, filekey, tarname):
        with open(tarname, 'rb') as tar_file:
            data = tar_file.read()
            self.send_training_backend(self.update, data)

    def request_backend_parse(self, update_id):
        backend = 'http://ab24300f.ngrok.io'
        update = requests.get(
            '{}/v2/repository/nlp/update_interpreters/{}/'.format(
                backend,
                update_id
            )
        ).json()
        return update

    def send_training_backend(self, update_id, botdata):
        backend = 'http://ab24300f.ngrok.io'
        update = requests.post(
            '{}/v2/repository/nlp/update_interpreters/'.format(
                backend
            ),
            data={
                "id": update_id,
                "bot_data": base64.b64encode(botdata).decode('utf8')
            }
        ).json()
        return update

    def retrieve(self, model_name, project, target_path):
        tar_name = self._tar_name(model_name, project)
        
        tar_data = base64.b64decode(
            self.request_backend_parse(self.update).get('bot_data')
        )
        tar_file = NamedTemporaryFile(suffix=tar_name, delete=False)
        tar_file.write(tar_data)
        tar_file.close()

        self._decompress(tar_file.name, target_path)
