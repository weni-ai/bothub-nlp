from collections import OrderedDict
from bothub_nlp_celery.app import nlp_language
from bothub.shared.utils.preprocessing.preprocessing_factory import PreprocessingFactory
import numpy as np


class WordSuggestion:
    def __init__(self):
        self.nlp = nlp_language
        self.to_replace_tags = ["VERB", "NOUN", "ADJ", "ADV", "INTJ", "PROPN"]
        self.n_highest = 50
        self.row2key = {row: key for key, row in self.nlp.vocab.vectors.key2row.items()}

    def most_similar(self, word, *, batch_size=1024, topn=1, sort=True):
        input_vector = self.nlp(word).vector.reshape(1, self.nlp.vocab.vectors.shape[1])
        best_rows = np.zeros((1, self.n_highest), dtype="i")
        scores = np.zeros((1, self.n_highest), dtype="f")

        # Work in batches, to avoid memory problems.
        for i in range(0, input_vector.shape[0], batch_size):
            batch = input_vector[i : i + batch_size]
            batch_norms = np.linalg.norm(batch, axis=1, keepdims=True)
            batch_norms[batch_norms == 0] = 1
            batch /= batch_norms
            sims = np.dot(batch, self.nlp.vocab.vectors.data.T)
            best_rows[i : i + batch_size] = np.argpartition(
                sims, -self.n_highest, axis=1
            )[
                :, -self.n_highest :
            ]  # get n_highest scores rows in O(n)
            scores[i : i + batch_size] = np.partition(sims, -self.n_highest, axis=1)[
                :, -self.n_highest :
            ]  # get n_highest scores in O(n)

            # sort the n_highest scores and best_rows
            if sort and topn >= 2:
                sorted_index = (
                    np.arange(scores.shape[0])[:, None][i : i + batch_size],
                    np.argsort(scores[i : i + batch_size], axis=1)[:, ::-1],
                )
                scores[i : i + batch_size] = scores[sorted_index]
                best_rows[i : i + batch_size] = best_rows[sorted_index]

        scores = np.around(scores, decimals=4, out=scores)
        scores = np.clip(scores, a_min=-1, a_max=1, out=scores)

        # get similar list of tuple (word, score) only if both input and candidate word is lower or large case
        similar_list = []
        for i in range(self.n_highest):
            row = best_rows[0][i]
            score = scores[0][i]
            candidate_word_vocab = self.nlp.vocab[self.row2key[row]]
            candidate_word = candidate_word_vocab.text
            if (
                candidate_word_vocab.is_lower == word.islower()
                and candidate_word != word
            ):
                similar_list.append((candidate_word, str(score)))
            if len(similar_list) >= topn:
                break
        return similar_list


def word_suggestion_text(text, n):
    if nlp_language is None:
        return "spacy model not loaded in this language"
    if nlp_language.vocab.vectors_length == 0:
        return "language not supported for this feature"

    preprocessor = PreprocessingFactory(remove_accent=False).factory()
    text = preprocessor.preprocess(text)
    similar_words = WordSuggestion().most_similar(text, topn=n)
    preprocessor = PreprocessingFactory(remove_accent=True).factory()
    similar_words = [(preprocessor.preprocess(word[0]), word[1]) for word in similar_words]

    return OrderedDict([("text", text), ("similar_words", similar_words)])
