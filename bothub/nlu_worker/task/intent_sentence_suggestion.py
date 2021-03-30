from collections import OrderedDict
from bothub_nlp_celery.app import nlp_language
from bothub.shared.utils.preprocessing.preprocessing_factory import PreprocessingFactory

import random

from .sentence_suggestion import SentenceSuggestion
from bothub.shared.utils.helpers import get_examples_request


class NonexistentIntentError(Exception):
    pass


def intent_sentence_suggestion_text(
    repository_version, repository_authorization, intent, percentage_to_replace, n
):
    if nlp_language is None:
        return "spacy model not loaded in this language"
    if nlp_language.vocab.vectors_length == 0:
        return "language not supported for this feature"

    intent_sentences = get_examples_request(repository_version, repository_authorization, intent=intent)
    intent_sentences = [el['text'] for el in intent_sentences]
    if len(intent_sentences) == 0:
        raise NonexistentIntentError()
    intent_sentences_sample = random.sample(intent_sentences, min(n, len(intent_sentences)))
    factor = n / len(intent_sentences_sample)

    preprocessor1 = PreprocessingFactory(remove_accent=False).factory()
    preprocessor2 = PreprocessingFactory(remove_accent=True).factory()

    suggested_sentences = []
    count = 0
    while len(suggested_sentences) < n:
        if count > n or count >= len(intent_sentences_sample):
            break
        generated_sentences = SentenceSuggestion().get_suggestions(
            preprocessor1.preprocess_text(intent_sentences_sample[count]),
            percentage_to_replace,
            random.randint(int(1 * factor), int(3 * factor))
        )
        for generated_sentence in generated_sentences:
            preprocessed_sentence = preprocessor2.preprocess_text(generated_sentence)
            if preprocessed_sentence not in intent_sentences:
                suggested_sentences.append(preprocessed_sentence)
        count += 1

    suggested_sentences = suggested_sentences[:n]

    return OrderedDict([("intent", intent), ("suggested_sentences", suggested_sentences)])
