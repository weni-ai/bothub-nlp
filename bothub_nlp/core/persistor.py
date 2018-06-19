from rasa_nlu.persistor import Persistor


class BothubPersistor(Persistor):
    def __init__(self, update=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update = update

    def _persist_tar(self, filekey, tarname):
        with open(tarname, 'rb') as tar_file:
            data = tar_file.read()
            self.update.save_training(data)
