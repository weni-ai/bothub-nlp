import re
from .preprocessing_interface import PreprocessingInterface
from unidecode import unidecode
import emoji
# -*- coding: utf-8 -*-


def de_emojify(phrase):
    phrase = emoji.demojize(phrase)
    return phrase


class PreprocessingBase(PreprocessingInterface):

    def preprocess(self, phrase: str = None):
        # removing accent and lowercasing characters
        phrase = de_emojify(phrase)
        return unidecode(phrase.lower())
