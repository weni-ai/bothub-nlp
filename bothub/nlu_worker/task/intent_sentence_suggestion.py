from collections import OrderedDict
from bothub_nlp_celery.app import nlp_language

import random
import numpy as np

from .sentence_suggestion import SentenceSuggestion
from bothub.shared.utils.helpers import get_examples_request


def get_intent_sentences(examples_list, intent):
    intent_sentences = []
    for example in examples_list:
        if example.get("intent") == intent:
            intent_sentences.append(example.get("text"))
    return intent_sentences


def intent_sentence_suggestion_text(
    repository_version, repository_authorization, intent, percentage_to_replace, n
):
    if nlp_language is None:
        return "spacy model not loaded in this language"
    if nlp_language.vocab.vectors_length == 0:
        return "language not supported for this feature"

    sentences = get_examples_request(repository_version, repository_authorization)
    intent_sentences = get_intent_sentences(sentences, intent)
    intent_sentences_sample = random.sample(intent_sentences, min(n, len(intent_sentences)))
    factor = n/len(intent_sentences_sample)

    suggested_sentences = []
    count = 0
    while len(suggested_sentences) < n:
        if count > n or count >= len(intent_sentences_sample):
            break
        generated_sentences = SentenceSuggestion().get_suggestions(
            intent_sentences_sample[count], percentage_to_replace, random.randint(int(1*factor), int(3*factor))
        )
        for generated_sentence in generated_sentences:
            if generated_sentence not in intent_sentences:
                suggested_sentences.append(generated_sentence)
        count += 1

    suggested_sentences = suggested_sentences[:n]

    return OrderedDict([("intent", intent), ("suggested_sentences", suggested_sentences)])
