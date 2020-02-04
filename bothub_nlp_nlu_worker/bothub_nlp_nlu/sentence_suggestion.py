from collections import OrderedDict
from thinc.neural.util import get_array_module
from bothub_nlp_celery.app import nlp_language
import random


def most_similar(nlp, self, queries, key, *, batch_size=1024, n=1, sort=True):
    """For each of the given vectors, find the n most similar entries
    to it, by cosine.
    Queries are by vector. Results are returned as a `(keys, best_rows,
    scores)` tuple. If `queries` is large, the calculations are performed in
    chunks, to avoid consuming too much memory. You can set the `batch_size`
    to control the size/space trade-off during the calculations.
    queries (ndarray): An array with one or more vectors.
    batch_size (int): The batch size to use.
    n (int): The number of entries to return for each query.
    sort (bool): Whether to sort the n entries returned by score.
    RETURNS (list(list(tuples)): The most similar entries as a list of `(word, score)`
    for each vector in queries

    """
    xp = get_array_module(self.data)

    similar_lists = []

    vectors = self.data / xp.linalg.norm(self.data, axis=1, keepdims=True)

    row2key = {row: key for key, row in self.key2row.items()}

    # Work in batches, to avoid memory problems.
    for i in range(0, queries.shape[0], batch_size):
        batch = queries[i : i + batch_size]
        batch /= xp.linalg.norm(batch, axis=1, keepdims=True)
        # batch   e.g. (1024, 300)
        # vectors e.g. (10000, 300)
        # sims    e.g. (1024, 10000)
        sims = xp.dot(batch, vectors.T)
        row_list = xp.argpartition(sims, -n, axis=1)[:, -n:]
        score_list = xp.partition(sims, -n, axis=1)[:, -n:]
        similar_list = []
        n_left = n
        for j in reversed(range(row_list[0].size)):
            row = row_list[0][j]
            score = score_list[0][j]
            word_vocab = nlp_language.vocab[row2key[row]]
            word = word_vocab.text
            if (
                word_vocab.is_lower == nlp.vocab[key].is_lower
                and word != nlp.vocab[key].text
            ):
                similar_list.append((word, score))
                n_left -= 1
            if n_left <= 0:
                break
        similar_lists.append(similar_list)

    if sort:
        for i in range(len(similar_lists)):
            similar_lists[i] = sorted(
                similar_lists[i], key=lambda tup: similar_lists[i][1]
            )

    return similar_lists


class SentenceSuggestion:
    def __init__(self, percentage_to_replace):
        self.nlp = nlp_language
        self.percentage_to_replace = percentage_to_replace
        self.to_replace_tags = ["VERB", "NOUN", "ADJ", "ADV", "INTJ", "PROPN"]

    def get_words_to_replace_idx(self, similar_words_json, word_list):
        word_list_size = len(word_list)
        for idx in list(similar_words_json):
            if len(similar_words_json[idx]["similar_words"]) == 0:
                del similar_words_json[idx]
        words_to_replace_idx = []
        n_words_to_replace = int(
            word_list_size * self.percentage_to_replace
        )  # number of words to replace
        replaceable_idx_list = list(similar_words_json)
        if n_words_to_replace < len(replaceable_idx_list):
            to_replace_idx_list = random.sample(
                range(len(replaceable_idx_list)), n_words_to_replace
            )
            for idx in to_replace_idx_list:
                words_to_replace_idx.append(replaceable_idx_list[idx])
        else:
            words_to_replace_idx = replaceable_idx_list
        return words_to_replace_idx

    def similar_words_json(self, sentence):
        nlp_sentence = self.nlp(sentence)
        similar_words_json = {}
        sentence_size = len(nlp_sentence)
        for i in range(sentence_size):
            try:
                word_json = {
                    "word": nlp_sentence[i].text,
                    "type": nlp_sentence[i].pos_,
                    "similar_words": [],
                }
                if nlp_sentence[i].pos_ in self.to_replace_tags:
                    similar_words = most_similar(
                        nlp_language,
                        self.nlp.vocab.vectors,
                        self.nlp(nlp_sentence[i].text).vector.reshape(1, 600),
                        self.nlp.vocab[nlp_sentence[i].text].orth,
                        n=6,
                    )[0]
                    similar_words_size = len(similar_words)
                    for j in range(similar_words_size):
                        nlp_similar = self.nlp(similar_words[j][0])
                        if (
                            len(nlp_similar) > 0
                            and nlp_similar[0].pos_ == nlp_sentence[i].pos_
                        ):
                            similar_json = {
                                "word": str(similar_words[j][0]),
                                "type": str(nlp_similar[0].pos_),
                                "relevance": str(similar_words[j][1]),
                            }
                            word_json["similar_words"].append(similar_json)
                similar_words_json[i] = word_json
            except KeyError:
                pass
        return similar_words_json

    def get_suggestions(self, sentence, n):  # main method
        similar_words_json = self.similar_words_json(sentence)
        suggested_sentences = []
        for _ in range(n):
            word_list = sentence.split(" ")
            words_to_replace_idx = self.get_words_to_replace_idx(
                similar_words_json, word_list
            )
            for replace_idx in words_to_replace_idx:
                similar_words_len = len(
                    similar_words_json[replace_idx]["similar_words"]
                )
                word_list[replace_idx] = similar_words_json[replace_idx][
                    "similar_words"
                ][random.randint(0, similar_words_len - 1)]["word"]
            suggested_sentences.append(" ".join(word_list))
        return suggested_sentences


def sentence_suggestion_text(text):
    similar_sentences = SentenceSuggestion(0.3).get_suggestions(text, 10)
    return OrderedDict([("text", text), ("suggested_sentences", similar_sentences)])
