import requests
import base64
from .backend import BaseBackend


class BothubBackend(BaseBackend):
    """
    Bothub instance as a backend
    """

    def request_backend_start_evaluation(self, update_id, repository_authorization):
        update = requests.get(
            '{}/v2/repository/nlp/authorization/evaluate/evaluations/?update_id={}'.format(
                self.backend,
                update_id
            ),
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def request_backend_create_evaluate_results(self, data, repository_authorization):
        update = requests.post(
            '{}/v2/repository/nlp/authorization/evaluate/evaluate_results/'.format(
                self.backend,
            ),
            data=data,
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def request_backend_create_evaluate_results_intent(
        self,
        data,
        repository_authorization):
        update = requests.post(
            '{}/v2/repository/nlp/authorization/evaluate/evaluate_results_intent/'.format(
                self.backend,
            ),
            data=data,
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def request_backend_create_evaluate_results_score(
        self,
        data,
        repository_authorization):
        update = requests.post(
            '{}/v2/repository/nlp/authorization/evaluate/evaluate_results_score/'.format(
                self.backend,
            ),
            data=data,
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def get_langs(self):
        langs = requests.get(
            '{}/v2/repository/nlp/authorization/langs/'.format(
                self.backend,
            )
        ).json()
        return langs

    def request_backend_parse(self, router, repository_authorization, language=None):
        update = requests.get(
            '{}/v2/repository/nlp/authorization/{}/{}/?language={}'.format(
                self.backend,
                router,
                repository_authorization,
                language
            ),
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def request_backend_parse_nlu(self, update_id, repository_authorization):
        update = requests.get(
            '{}/v2/repository/nlp/update_interpreters/{}/'.format(
                self.backend,
                update_id
            ),
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def request_backend_start_training_nlu(self, update_id, by, repository_authorization):
        update = requests.post(
            '{}/v2/repository/nlp/authorization/train/start_training/'.format(
                self.backend
            ),
            data={
                "update_id": update_id,
                "by_user": by
            },
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def request_backend_get_entities_nlu(self, update_id, language, example_id, repository_authorization):
        update = requests.get(
            '{}/v2/repository/nlp/authorization/train/get_entities/?update_id={}&language={}&example_id={}'.format(
                self.backend,
                update_id,
                language,
                example_id
            ),
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def request_backend_get_entities_label_nlu(self, update_id, language, example_id, repository_authorization):
        update = requests.get(
            '{}/v2/repository/nlp/authorization/train/get_entities_label/?update_id={}&language={}&example_id={}'.format(
                self.backend,
                update_id,
                language,
                example_id
            ),
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def request_backend_get_text_nlu(self, update_id, language, example_id, repository_authorization):
        update = requests.get(
            '{}/v2/repository/nlp/authorization/train/get_text/?update_id={}&language={}&example_id={}'.format(
                self.backend,
                update_id,
                language,
                example_id
            ),
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def request_backend_trainfail_nlu(self, update_id, repository_authorization):
        update = requests.post(
            '{}/v2/repository/nlp/authorization/train/train_fail/'.format(
                self.backend
            ),
            data={
                'update_id': update_id
            },
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def request_backend_traininglog_nlu(self, update_id, training_log, repository_authorization):
        update = requests.post(
            '{}/v2/repository/nlp/authorization/train/training_log/'.format(
                self.backend
            ),
            data={
                'update_id': update_id,
                'training_log': training_log
            },
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def request_backend_parse_nlu_persistor(self, update_id, repository_authorization):
        update = requests.get(
            '{}/v2/repository/nlp/update_interpreters/{}/'.format(
                self.backend,
                update_id
            ),
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def send_training_backend_nlu_persistor(self, update_id, botdata, repository_authorization):
        update = requests.post(
            '{}/v2/repository/nlp/update_interpreters/'.format(
                self.backend
            ),
            data={
                "id": update_id,
                "bot_data": base64.b64encode(botdata).decode('utf8')
            },
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def request_backend_repository_entity_nlu_parse(self, update_id, repository_authorization, entity):
        update = requests.get(
            '{}/v2/repository/nlp/authorization/parse/repository_entity/?update_id={}&entity={}'.format(
                self.backend,
                update_id,
                entity
            ),
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update