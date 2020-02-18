from collections import OrderedDict
from thinc.neural.util import get_array_module
from bothub_nlp_celery.app import nlp_language
import random
import time


class SentenceSuggestion:
    def __init__(self):
        self.nlp = nlp_language
        self.to_replace_tags = ["VERB", "NOUN", "ADJ", "ADV", "INTJ", "PROPN"]
        self.row2key = {row: key for key, row in self.nlp.vocab.vectors.key2row.items()}

    def get_words_to_replace_idx(self, similar_words_json, word_list, percentage_to_replace):
        word_list_size = len(word_list)
        for idx in list(similar_words_json):
            if len(similar_words_json[idx]["similar_words"]) == 0:
                del similar_words_json[idx]
        words_to_replace_idx = []
        n_words_to_replace = int(
            word_list_size * percentage_to_replace
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
                    similar_words = self.most_similar(nlp_sentence[i].text, n=6)[0]
                    similar_words_size = len(similar_words)
                    for j in range(similar_words_size):
                        nlp_similar = self.nlp(similar_words[j][0])
                        if len(nlp_similar) > 0 and nlp_similar[0].pos_ == nlp_sentence[i].pos_:
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

    def get_suggestions(self, sentence, percentage_to_replace, n):  # main method
        similar_words_json = self.similar_words_json(sentence)
        suggested_sentences = []
        for _ in range(n):
            word_list = sentence.split(" ")
            words_to_replace_idx = self.get_words_to_replace_idx(
                similar_words_json, word_list, percentage_to_replace
            )
            for replace_idx in words_to_replace_idx:
                similar_words_len = len(
                    similar_words_json[replace_idx]["similar_words"]
                )
                word_list[replace_idx] = similar_words_json[replace_idx][
                    "similar_words"
                ][random.randint(0, similar_words_len - 1)]["word"]
            suggested_sentences.append(" ".join(word_list))
        suggested_sentences = list(set(suggested_sentences))  # Remove duplicates
        return suggested_sentences

    def words_to_vecs(self, xp, words):
        if isinstance(words, str):
            return self.nlp(words).vector.reshape(1, self.nlp.vocab.vectors.shape[1])
        queries = []
        for word in words:
            queries.append(self.nlp(word).vector)
        return xp.array(queries)

    def idx_to_word(self, idx):
        return self.nlp.vocab[self.row2key[idx]].text

    def most_similar(self, words, *, batch_size=1024, n=1, sort=True):
        start = time.time()
        xp = get_array_module(self.nlp.vocab.vectors.data)
        queries = self.words_to_vecs(xp, words)
        best_rows = xp.zeros((queries.shape[0], n), dtype='i')
        scores = xp.zeros((queries.shape[0], n), dtype='f')
        # Work in batches, to avoid memory problems.
        print('setup in: ', time.time() - start)
        start_iter = time.time()
        for i in range(0, queries.shape[0], batch_size):
            batch = queries[i: i + batch_size]
            batch_norms = xp.linalg.norm(batch, axis=1, keepdims=True)
            batch_norms[batch_norms == 0] = 1
            batch /= batch_norms
            sims = xp.dot(batch, self.nlp.vocab.vectors.data.T)
            best_rows[i:i + batch_size] = xp.argpartition(sims, -n, axis=1)[:, -n:]
            scores[i:i + batch_size] = xp.partition(sims, -n, axis=1)[:, -n:]

        if sort and n >= 2:
            sorted_index = xp.arange(scores.shape[0])[:, None][i:i + batch_size], xp.argsort(scores[i:i + batch_size],
                                                                                             axis=1)[:, ::-1]
            scores[i:i + batch_size] = scores[sorted_index]
            best_rows[i:i + batch_size] = best_rows[sorted_index]
        print('iter in: ', time.time() - start_iter)
        start_end = time.time()
        scores = xp.around(scores, decimals=4, out=scores)
        scores = xp.clip(scores, a_min=-1, a_max=1, out=scores)
        scores_list = scores.tolist()
        best_rows = xp.vectorize(self.idx_to_word)(best_rows)
        rows_list = best_rows.tolist()
        similar_tuple_list = []
        size = len(scores_list)
        for i in range(size):
            similar_tuple_list.append(list(zip(rows_list[i], scores_list[i])))

        for tuple_list in similar_tuple_list:
            print(tuple_list)
        print('wrapping up in: ', time.time() - start_end)
        return similar_tuple_list


def sentence_suggestion_text(text):
    if nlp_language.vocab.vectors_length == 0:
        return 'language not supported for this feature'
    similar_sentences = SentenceSuggestion().get_suggestions(text, 0.3, 10)
    return OrderedDict([("text", text), ("suggested_sentences", similar_sentences)])
