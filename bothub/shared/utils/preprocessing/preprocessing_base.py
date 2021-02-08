import logging
from unidecode import unidecode
import emoji
import re

logger = logging.getLogger(__name__)


class PreprocessingBase(object):
    emoji_contractions = {}

    def __init__(self, remove_accent=True):
        self.remove_accent = remove_accent

    def preprocess(self, phrase: str = None):
        phrase = self.emoji_handling(phrase)
        phrase = self.default_preprocessing(phrase)
        return phrase

    def default_preprocessing(self, phrase: str = None):

        if phrase is None:
            raise ValueError

        # remove apostrophe from the phrase (important be first than s_regex regex)
        for APOSTROPHE in ["'", "`"]:
            phrase = phrase.replace(APOSTROPHE, "")

        # lowercasing characters
        phrase = phrase.lower()

        if self.remove_accent:
            phrase = unidecode(phrase)

        return phrase

    @staticmethod
    def extract_emoji_text(code):
        """
        :param code: is a emoji_code string ex:  :smile_face:
        :return: "smile face"
        """
        if code is None or code[0] != ':' or code[-1] != ':':
            raise ValueError

        code = code[1:len(code) - 1]
        text = ' '.join(code.split('_'))
        return text

    def emoji_handling(self, phrase: str = None):
        # turn emojis into text codes
        phrase = emoji.demojize(phrase)

        regex_emoji = r":[A-Za-z0-9\-_]+:"
        emoji_codes = re.findall(regex_emoji, phrase)
        for code in emoji_codes:
            try:
                phrase = re.sub(code, self.emoji_contractions[code], phrase)
            except KeyError:
                phrase = re.sub(code, self.extract_emoji_text(code), phrase)

        return phrase
