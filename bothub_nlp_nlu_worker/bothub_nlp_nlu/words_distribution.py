from collections import Counter, OrderedDict

from .utils import get_examples_request


def words_distribution_text(repository_version, language, repository_authorization):
    examples_list = get_examples_request(repository_version, repository_authorization)

    all_intents = []  # the list of all words
    intents = {}  # all the words separated by intent
    all_frequencies = {}  # the count of all words
    frequencies = {}  # the count of words separated by intent

    for example in examples_list:
        text = example.get("text")
        intent = example.get("intent")
        for word in text.split():
            all_intents.append(word.lower())
            if intent in intents:
                intents[intent].append(word.lower())
            else:
                intents[intent] = [word.lower()]

    all_frequencies = Counter(all_intents)

    for intent in intents:
        frequencies[intent] = Counter(intents[intent])

    for intent in frequencies:
        for n_tuple in frequencies[intent].most_common():
            word = n_tuple[0]
            try:
                frequencies[intent][word] = (
                    frequencies[intent][word] / all_frequencies[word] * 100
                )
            except ZeroDivisionError:  # pragma: no cover
                continue  # pragma: no cover

    ordered_frequencies = {}

    for intent in frequencies:
        if intent not in ordered_frequencies:
            ordered_frequencies[intent] = OrderedDict()
        for n_tuple in frequencies[intent].most_common():
            word = n_tuple[0]
            ordered_frequencies[intent][word] = frequencies[intent][word]

    return {"words": ordered_frequencies}
