# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


from abc import ABCMeta, abstractmethod


class BaseBackend(object):
    __metaclass__ = ABCMeta

    def __init__(self, backend):
        self.backend = backend

    @abstractmethod
    def request_backend_start_evaluation(self, update_id, repository_authorization):
        pass

    @abstractmethod
    def request_backend_create_evaluate_results(self, data, repository_authorization):
        pass

    @abstractmethod
    def request_backend_create_evaluate_results_intent(self, data, repository_authorization):
        pass

    @abstractmethod
    def request_backend_create_evaluate_results_score(self, data, repository_authorization):
        pass

    @abstractmethod
    def get_langs(self):
        pass

    @abstractmethod
    def request_backend_parse(self, router, repository_authorization, language=None):
        pass

    @abstractmethod
    def request_backend_parse_nlu(self, update_id, repository_authorization):
        pass

    @abstractmethod
    def request_backend_start_training_nlu(self, update_id, by, repository_authorization):
        pass
    
    @abstractmethod
    def request_backend_get_entities_nlu(self, update_id, language, example_id, repository_authorization):
        pass

    @abstractmethod
    def request_backend_get_entities_label_nlu(self, update_id, language, example_id, repository_authorization):
        pass

    @abstractmethod
    def request_backend_get_text_nlu(self, update_id, language, example_id, repository_authorization):
        pass

    @abstractmethod
    def request_backend_trainfail_nlu(self, update_id, repository_authorization):
        pass

    @abstractmethod
    def request_backend_traininglog_nlu(self, update_id, training_log, repository_authorization):
        pass

    @abstractmethod
    def request_backend_parse_nlu_persistor(self, update_id, repository_authorization):
        pass

    @abstractmethod
    def send_training_backend_nlu_persistor(self, update_id, botdata, repository_authorization):
        pass

    @abstractmethod
    def request_backend_repository_entity_nlu_parse(self, update_id, repository_authorization, entity):
        pass