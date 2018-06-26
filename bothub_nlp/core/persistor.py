from tempfile import NamedTemporaryFile

from rasa_nlu.persistor import Persistor


class BothubPersistor(Persistor):
    def __init__(self, update=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update = update

    def _persist_tar(self, filekey, tarname):
        with open(tarname, 'rb') as tar_file:
            data = tar_file.read()
            self.update.save_training(data)

    def retrieve(self, model_name, project, target_path):
        tar_name = self._tar_name(model_name, project)

        tar_data = self.update.get_bot_data()
        tar_file = NamedTemporaryFile(suffix=tar_name, delete=False)
        tar_file.write(tar_data)
        tar_file.close()

        self._decompress(tar_file.name, target_path)
