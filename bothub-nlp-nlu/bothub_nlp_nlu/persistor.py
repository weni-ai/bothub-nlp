import base64
import requests
from tempfile import NamedTemporaryFile

from rasa_nlu.persistor import Persistor
from decouple import config


class BothubPersistor(Persistor):
    def __init__(self, update=None, repository_authorization=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update = update
        self.repository_authorization = repository_authorization

    def _persist_tar(self, filekey, tarname):
        with open(tarname, 'rb') as tar_file:
            data = tar_file.read()
            self.send_training_backend(self.update, data, self.repository_authorization)

    def request_backend_parse(self, update_id, repository_authorization):
        update = requests.get(
            '{}/v2/repository/nlp/update_interpreters/{}/'.format(
                config('BOTHUB_ENGINE_URL', default='https://api.bothub.it'),
                update_id
            ),
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def send_training_backend(self, update_id, botdata, repository_authorization):
        update = requests.post(
            '{}/v2/repository/nlp/update_interpreters/'.format(
                config('BOTHUB_ENGINE_URL', default='https://api.bothub.it')
            ),
            data={
                "id": update_id,
                "bot_data": base64.b64encode(botdata).decode('utf8')
            },
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def retrieve(self, model_name, project, target_path):
        print(self.repository_authorization)
        tar_name = self._tar_name(model_name, project)
        
        tar_data = base64.b64decode(
            self.request_backend_parse(self.update, self.repository_authorization).get('bot_data')
        )
        tar_file = NamedTemporaryFile(suffix=tar_name, delete=False)
        tar_file.write(tar_data)
        tar_file.close()

        self._decompress(tar_file.name, target_path)
