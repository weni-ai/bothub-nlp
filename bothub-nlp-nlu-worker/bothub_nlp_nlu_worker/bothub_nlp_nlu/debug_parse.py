from collections import OrderedDict
from rasa.nlu.test import remove_pretrained_extractors
from lime.lime_text import LimeTextExplainer
from .utils import update_interpreters
from .utils import backend
import numpy as np
import json


class DebugSentenceLime:
    def __init__(self, interpreter, intention_names):
        self.interpreter = interpreter
        self.interpreter.pipeline = remove_pretrained_extractors(self.interpreter.pipeline)
        self.intention_names = intention_names

    def show_results(self, text, result_per_word, result_per_intent, elapsed_time, is_detailed):
        response_json = self.interpreter.parse(text)
        print('\n\nText: ', text, '\n')
        print('Model Prediction: ', self.interpreter.parse(text)['intent']['name'])
        for intent in response_json['intent_ranking']:
            print('    intent: ', intent['name'], 'confidence: ', round(float(intent['confidence']), 2))

        print('LIME DEBUG')
        print('\nGeneral Debug(results per word):')
        for word in result_per_word:
            word_str = '{:<10}'.format(word)
            if len(result_per_word[word]) > 0:
                intent_str = '{:<15}'.format(result_per_word[word][0]['intent'])
                relevance_str = '{:<10}'.format(round(result_per_word[word][0]['relevance'], 3))
                print('     \'word\':', word_str, ' \'intent\':', intent_str, ' \'relevance\': ', relevance_str)
            else:
                print('     \'word\':', word_str, ' \'intent\': none          \'relevance\': none')
        print()
        if is_detailed:
            print('Detailed Debug 1(results per word):')
            for word in result_per_word:
                print('    word: ', word)
                for word_result in result_per_word[word]:
                    intent_str = '{:<15}'.format(word_result['intent'])
                    relevance_str = '{:<15}'.format(round(word_result['relevance'], 2))
                    print('        \'intent\':', intent_str, ' \'relevance\':', relevance_str)
                print()

            print('Detailed Debug 2(results per intention):')
            for intent in result_per_intent:
                print('    intention: ', intent)
                for intent_result in result_per_intent[intent]:
                    if 'word' in intent_result:
                        intent_str = '{:<15}'.format(intent_result['word'])
                        relevance_str = '{:<15}'.format(round(intent_result['relevance'], 3))
                        print('        \'word\':', intent_str, ' \'relevance\':', relevance_str)
                    else:
                        print('        \'sum\':', intent_result['sum'])
                print()

        print('Elapsed Time: ', str(elapsed_time), '\n')

    def parse(self, text_list):
        result_list = []
        for text in text_list:
            result_json = self.interpreter.parse(text)

            idx_dict = {}  # fixing intent name to a index ex: {'violence': 0, 'immigration': 1, ... }
            size = len(self.intention_names)
            for i in range(size):
                idx_dict[self.intention_names[i]] = i

            intent_list = [0] * len(self.intention_names)
            intent_name_list = [''] * len(self.intention_names)
            size = len(result_json['intent_ranking'])
            for i in range(size):
                intent_name = result_json['intent_ranking'][i]['name']
                intent_list[idx_dict[intent_name]] = result_json['intent_ranking'][i]['confidence']
                intent_name_list[idx_dict[intent_name]] = result_json['intent_ranking'][i]['name']

            prob_array = np.array(intent_list)
            prob_array = prob_array.reshape((1, len(intent_list)))
            result_list.append(prob_array)

        result_array = result_list[0]
        for i in range(1, len(result_list)):
            result_array = np.vstack([result_array, result_list[i]])
        return result_array

    def get_result_per_word(self, text, num_samples):
        explainer = LimeTextExplainer(class_names=self.intention_names)
        labels = list(range(len(self.intention_names)))  # List
        exp = explainer.explain_instance(text, self.parse, num_features=6, labels=labels, num_samples=num_samples)
        result_per_word = {}
        for i in labels:
            for j in exp.as_list(label=i):
                # j = (word, relevance)
                if j[0] not in result_per_word:
                    result_per_word[j[0]] = []
                result_per_word[j[0]].append({'intent': self.intention_names[i], 'relevance': j[1] * 100})
        for word in result_per_word:
            result_per_word[word] = sorted(result_per_word[word], key=lambda k: k['relevance'], reverse=True)
        print(json.dumps(result_per_word, indent=2))
        return result_per_word

    def get_result_per_intent(self, text, num_samples):
        explainer = LimeTextExplainer(class_names=self.intention_names)
        labels = list(range(len(self.intention_names)))  # List
        exp = explainer.explain_instance(text, self.parse, num_features=6, labels=labels, num_samples=num_samples)
        result_per_intent = {}
        for intent in self.intention_names:
            result_per_intent[intent] = []
        for i in labels:
            intent_sum = 0
            for j in exp.as_list(label=i):
                result_per_intent[self.intention_names[i]].append({'word': j[0], 'relevance': j[1] * 100})
                intent_sum += j[1]
            result_per_intent[self.intention_names[i]].append({'sum': intent_sum, 'relevance': -1})
        for intent in result_per_intent:
            result_per_intent[intent] = sorted(result_per_intent[intent], key=lambda k: k['relevance'], reverse=True)

        return result_per_intent


def get_intention_list(repository_authorization):
    info = backend().request_backend_parse("info", repository_authorization)
    if not info.get('detail'):
        return info["intents_list"]


def format_debug_parse_output(result_per_word, r):
    out = OrderedDict(
        [
            ("intent", r.get("intent", None)),
            ("words", result_per_word),
        ]
    )
    return out


def debug_parse_text(
    repository_version, repository_authorization, text, use_cache=True
):
    interpreter = update_interpreters.get(
        repository_version, repository_authorization, use_cache=use_cache
    )
    r = interpreter.parse(text)

    intention_names = get_intention_list(repository_authorization)

    result_per_word = DebugSentenceLime(interpreter, intention_names).get_result_per_word(text, 200)

    return format_debug_parse_output(result_per_word, r)

