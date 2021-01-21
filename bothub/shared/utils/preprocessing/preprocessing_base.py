import logging
from unidecode import unidecode
import emoji
import re

logger = logging.getLogger(__name__)


class PreprocessingBase(object):
    emoji_contractions = {}

    def preprocess(self, phrase: str = None):
        phrase = self.default_preprocessing(phrase)
        phrase = self.emoji_handling(phrase)
        return phrase

    @staticmethod
    def default_preprocessing(phrase: str = None):

        if phrase is None:
            raise ValueError

        # remove apostrophe from the phrase (important be first than s_regex regex)
        for APOSTROPHE in ["'", "`"]:
            phrase = phrase.replace(APOSTROPHE, "")

        # removing accent and lowercasing characters
        phrase = unidecode(phrase.lower())

        return phrase

    @staticmethod
    def extract_emoji_text(code):
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
