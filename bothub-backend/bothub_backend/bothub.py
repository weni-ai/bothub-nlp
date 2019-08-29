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

    def request_backend_create_evaluateresults(
        self,
        update_id, 
        matrix_chart, 
        confidence_chart, 
        log,
        intentprecision,
        intentf1_score,
        intentaccuracy,
        entityprecision,
        entityf1_score,
        entityaccuracy,
        repository_authorization):
        update = requests.post(
            '{}/v2/repository/nlp/authorization/evaluate/evaluateresults/'.format(
                self.backend,
            ),
            data={
                'update_id': update_id,
                'matrix_chart': matrix_chart,
                'confidence_chart': confidence_chart,
                'log': log,
                'intentprecision': intentprecision,
                'intentf1_score': intentf1_score,
                'intentaccuracy': intentaccuracy,
                'entityprecision': entityprecision,
                'entityf1_score': entityf1_score,
                'entityaccuracy': entityaccuracy
            },
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def request_backend_create_evaluateresultsintent(
        self,
        evaluate_id, 
        precision, 
        recall, 
        f1_score,
        support,
        intent_key,
        repository_authorization):
        update = requests.post(
            '{}/v2/repository/nlp/authorization/evaluate/evaluateresultsintent/'.format(
                self.backend,
            ),
            data={
                'evaluate_id': evaluate_id,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'support': support,
                'intent_key': intent_key
            },
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update

    def request_backend_create_evaluateresultsscore(
        self,
        evaluate_id, 
        update_id, 
        precision, 
        recall,
        f1_score,
        support,
        entity_key,
        repository_authorization):
        update = requests.post(
            '{}/v2/repository/nlp/authorization/evaluate/evaluateresultsscore/'.format(
                self.backend,
            ),
            data={
                'evaluate_id': evaluate_id,
                'update_id': update_id,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'support': support,
                'entity_key': entity_key
            },
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
            '{}/v2/repository/nlp/authorization/train/starttraining/'.format(
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
            '{}/v2/repository/nlp/authorization/train/getentities/?update_id={}&language={}&example_id={}'.format(
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
            '{}/v2/repository/nlp/authorization/train/getentitieslabel/?update_id={}&language={}&example_id={}'.format(
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
            '{}/v2/repository/nlp/authorization/train/gettext/?update_id={}&language={}&example_id={}'.format(
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
            '{}/v2/repository/nlp/authorization/train/trainfail/'.format(
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
            '{}/v2/repository/nlp/authorization/train/traininglog/'.format(
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
            '{}/v2/repository/nlp/authorization/parse/repositoryentity/?update_id={}&entity={}'.format(
                self.backend,
                update_id,
                entity
            ),
            headers={'Authorization': 'Bearer {}'.format(repository_authorization)}
        ).json()
        return update