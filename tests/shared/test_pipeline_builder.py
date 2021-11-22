import unittest
import os

import sys
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from bothub.shared.utils.pipeline_builder import PipelineBuilder
from rasa.nlu.registry import class_from_module_path


class TestPipelineBuilder(unittest.TestCase):
    def setUp(self, *args):
        self.update = {
            'language': 'en',
            'repository_version': 47,
            'repository_uuid': '1d8e0d6f-1941-42a3-84c5-788706c7072e',
            'intent': [4, 5],
            'algorithm': 'transformer_network_diet_bert',
            'use_name_entities': False,
            'use_competing_intents': False,
            'use_analyze_char': False,
            'total_training_end': 0,
            'dataset_size': 15000,
        }

        self.pipeline_builder = PipelineBuilder(self.update)

        list_dir = os.listdir()
        while 'bert_english' not in list_dir:
            os.chdir("../")
            list_dir = os.listdir()

    def test__add_spacy_nlp(self):
        component_name = self.pipeline_builder._add_spacy_nlp().get('name')
        if '.' in component_name:
            class_from_module_path(component_name)

    def test__add_whitespace_tokenizer(self):
        component_name = self.pipeline_builder._add_whitespace_tokenizer().get('name')
        if '.' in component_name:
            class_from_module_path(component_name)

    def test__add_preprocessing(self):
        component_name = self.pipeline_builder._add_preprocessing().get('name')
        if '.' in component_name:
            class_from_module_path(component_name)

    def test__add_regex_entity_extractor(self):
        component_name = self.pipeline_builder._add_regex_entity_extractor().get('name')
        if '.' in component_name:
            class_from_module_path(component_name)

    def test__add_countvectors_featurizer(self):
        components_list = self.pipeline_builder._add_countvectors_featurizer()
        for component in components_list:
            component_name = component.get('name')
            if '.' in component_name:
                class_from_module_path(component_name)

    def test__add_legacy_countvectors_featurizer(self):
        component_name = self.pipeline_builder._add_legacy_countvectors_featurizer().get('name')
        if '.' in component_name:
            class_from_module_path(component_name)

    def test__add_microsoft_entity_extractor(self):
        component_name = self.pipeline_builder._add_microsoft_entity_extractor().get('name')
        if '.' in component_name:
            class_from_module_path(component_name)

    def test__add_embedding_intent_classifier(self):
        component_name = self.pipeline_builder._add_embedding_intent_classifier().get('name')
        if '.' in component_name:
            class_from_module_path(component_name)

    def test__add_diet_classifier(self):
        component_name = self.pipeline_builder._add_diet_classifier().get('name')
        if '.' in component_name:
            class_from_module_path(component_name)

    def test__legacy_internal_config(self):
        components_list = self.pipeline_builder._legacy_internal_config()
        for component in components_list:
            component_name = component.get('name')
            if '.' in component_name:
                class_from_module_path(component_name)

    def test__legacy_external_config(self):
        components_list = self.pipeline_builder._legacy_external_config()
        for component in components_list:
            component_name = component.get('name')
            if '.' in component_name:
                class_from_module_path(component_name)

    def test__transformer_network_diet_config(self):
        components_list = self.pipeline_builder._transformer_network_diet_config()
        for component in components_list:
            component_name = component.get('name')
            if '.' in component_name:
                class_from_module_path(component_name)

    def test__transformer_network_diet_word_embedding_config(self):
        components_list = self.pipeline_builder._transformer_network_diet_word_embedding_config()
        for component in components_list:
            component_name = component.get('name')
            if '.' in component_name:
                class_from_module_path(component_name)

    def test__transformer_network_diet_bert_config(self):
        components_list = self.pipeline_builder._transformer_network_diet_bert_config()
        for component in components_list:
            component_name = component.get('name')
            if '.' in component_name:
                class_from_module_path(component_name)

    def test_unexisting_model_language(self):
        update = {
            'language': 'unexisting',
            'algorithm': 'neural_network_external',
            'use_name_entities': False,
            'dataset_size': 15000,
        }
        pipeline_builder = PipelineBuilder(update)
        self.assertEqual(pipeline_builder.model, None)

        update['algorithm'] = 'transformer_network_diet'
        pipeline_builder = PipelineBuilder(update)
        self.assertEqual(pipeline_builder.model, None)

        update['algorithm'] = 'neural_network_internal'
        pipeline_builder = PipelineBuilder(update)
        self.assertEqual(pipeline_builder.model, None)

        update = {
            'language': 'en',
            'algorithm': 'transformer_network_diet_bert',
            'use_name_entities': True,
            'dataset_size': 15000,
        }
        pipeline_builder = PipelineBuilder(update)
        self.assertEqual(pipeline_builder.model, 'BERT')

    def test__dynamic_epochs(self):
        self.update["dataset_size"] = 10000
        self.pipeline_builder = PipelineBuilder(self.update)
        result_epochs = self.pipeline_builder._calculate_epochs_number(
            100,
            self.pipeline_builder._epoch_factor_function1
        )
        self.assertEqual(result_epochs, 100)

        self.update["dataset_size"] = 15000
        self.pipeline_builder = PipelineBuilder(self.update)
        result_epochs = self.pipeline_builder._calculate_epochs_number(
            100,
            self.pipeline_builder._epoch_factor_function1
        )
        self.assertLess(result_epochs, 100)
        self.assertGreater(result_epochs, 0)

        self.update["dataset_size"] = 0
        self.pipeline_builder = PipelineBuilder(self.update)
        result_epochs = self.pipeline_builder._calculate_epochs_number(
            100,
            self.pipeline_builder._epoch_factor_function1
        )
        self.assertEqual(result_epochs, 100)

