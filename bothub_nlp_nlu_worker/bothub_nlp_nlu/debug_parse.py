import numpy as np
from collections import OrderedDict
from lime.lime_text import LimeTextExplainer
from rasa.nlu import __version__ as rasa_version
from rasa.nlu.test import remove_pretrained_extractors
from .parse import minimal_entity
from .utils import backend
from .utils import update_interpreters


class DebugSentenceLime:
    def __init__(self, interpreter, intention_names):
        self.interpreter = interpreter
        self.interpreter.pipeline = remove_pretrained_extractors(
            self.interpreter.pipeline
        )
        self.intention_names = intention_names

    def parse(self, text_list):
        result_list = []
        for text in text_list:
            result_json = self.interpreter.parse(text)

            idx_dict = (
                {}
            )  # fixing intent name to a index ex: {'violence': 0, 'immigration': 1, ... }
            size = len(self.intention_names)
            for i in range(size):
                idx_dict[self.intention_names[i]] = i

            intent_list = [0] * len(self.intention_names)
            intent_name_list = [""] * len(self.intention_names)
            size = len(result_json.get("intent_ranking", []))
            for i in range(size):
                intent_name = result_json.get("intent_ranking")[i].get("name")
                intent_list[idx_dict[intent_name]] = result_json.get("intent_ranking")[
                    i
                ].get("confidence")
                intent_name_list[idx_dict[intent_name]] = result_json.get(
                    "intent_ranking"
                )[i].get("name")

            prob_array = np.array(intent_list)
            prob_array = prob_array.reshape((1, len(intent_list)))
            result_list.append(prob_array)

        result_array = result_list[0]
        for i in range(1, len(result_list)):
            result_array = np.vstack([result_array, result_list[i]])
        return result_array

    def get_result_per_word(self, text, num_samples):
        if not self.intention_names:
            return {}
        explainer = LimeTextExplainer(class_names=self.intention_names)
        labels = list(range(len(self.intention_names)))  # List
        try:
            exp = explainer.explain_instance(
                text, self.parse, num_features=6, labels=labels, num_samples=num_samples
            )
        except ValueError:
            labels = []
        result_per_word = {}
        for label in labels:
            for j in exp.as_list(label=label):
                if j[0] not in result_per_word:
                    result_per_word[j[0]] = []
                result_per_word[j[0]].append(
                    {"intent": self.intention_names[label], "relevance": j[1] * 100}
                )
        for word in result_per_word:
            result_per_word[word] = sorted(
                result_per_word[word], key=lambda k: k.get("relevance"), reverse=True
            )
        return result_per_word

    def get_result_per_intent(self, text, num_samples):
        explainer = LimeTextExplainer(class_names=self.intention_names)
        labels = list(range(len(self.intention_names)))  # List
        exp = explainer.explain_instance(
            text, self.parse, num_features=6, labels=labels, num_samples=num_samples
        )
        result_per_intent = {}
        for intent in self.intention_names:
            result_per_intent[intent] = []
        for i in labels:
            intent_sum = 0
            for j in exp.as_list(label=i):
                result_per_intent[self.intention_names[i]].append(
                    {"word": j[0], "relevance": j[1] * 100}
                )
                intent_sum += j[1]
            result_per_intent[self.intention_names[i]].append(
                {"sum": intent_sum, "relevance": -1}
            )
        for intent in result_per_intent:
            result_per_intent[intent] = sorted(
                result_per_intent[intent],
                key=lambda k: k.get("relevance"),
                reverse=True,
            )

        return result_per_intent


def get_intention_list(repository_authorization):
    info = backend().request_backend_info(repository_authorization)
    if not info.get("detail"):
        return info.get("intents_list")
    return []


def format_debug_parse_output(result_per_word, r):
    entities = r.get("entities")
    formatted_entities = []
    for entity in entities:
        formatted_entities.append(minimal_entity(entity))
    for word in result_per_word:
        result_per_word[word] = sorted(
            result_per_word[word], key=lambda k: k["relevance"], reverse=True
        )
    result_per_word = OrderedDict(
        sorted(
            result_per_word.items(), key=lambda t: t[1][0]["relevance"], reverse=True
        )
    )
    out = OrderedDict(
        [
            ("intent", r.get("intent", None)),
            ("words", result_per_word),
            ("entities", formatted_entities),
        ]
    )
    return out


def n_samples_by_sentence_lenght(sentence):
    word_count = len(sentence.split(" "))
    return word_count * 200


def debug_parse_text(
    repository_version, repository_authorization, text, use_cache=True
):
    interpreter = update_interpreters.get(
        repository_version, repository_authorization, rasa_version, use_cache=use_cache
    )
    r = interpreter.parse(text)

    intention_names = get_intention_list(repository_authorization)

    result_per_word = DebugSentenceLime(
        interpreter, intention_names
    ).get_result_per_word(text, n_samples_by_sentence_lenght(text))

    return format_debug_parse_output(result_per_word, r)
