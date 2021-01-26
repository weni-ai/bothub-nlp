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

    examples_list = get_examples_request(repository_version, repository_authorization)
    intent_sentences = get_intent_sentences(examples_list, intent)
    intent_sentences = random.sample(intent_sentences, min(n, len(intent_sentences)))

    similar_sentences = []
    count = 0
    while len(similar_sentences) < n:
        if count > n or count >= len(intent_sentences):
            break
        sentences = SentenceSuggestion().get_suggestions(
            intent_sentences[count], percentage_to_replace, random.randint(2, 4)
        )
        similar_sentences.extend(sentences)
        count += 1

    similar_sentences = similar_sentences[:n]
    # remove intent_sentences that are in similar_sentences
    similar_sentences = list(set(similar_sentences) - set(intent_sentences))

    return OrderedDict([("intent", intent), ("suggested_sentences", similar_sentences)])
