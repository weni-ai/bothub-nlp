import logging
from unidecode import unidecode
import emoji
import re
from rasa.nlu.training_data import Message

logger = logging.getLogger(__name__)


class PreprocessingBase(object):
    emoji_contractions = {}
    apostrophes = ["'", "`", "’"]

    def __init__(self, remove_accent=True):
        self.remove_accent = remove_accent

    def preprocess_text(self, phrase: str) -> str:
        phrase = self.emoji_handling(phrase)
        phrase, _ = self.default_preprocessing(phrase)
        return phrase

    def preprocess(self, example: Message) -> Message:
        phrase = example.text
        entities = example.data.get('entities')

        phrase = self.emoji_handling(phrase)
        phrase, entities = self.default_preprocessing(phrase, entities)

        example.text = phrase
        if entities:
            example.data['entities'] = entities

        return example

    def _handle_entities(self, phrase, entities):
        # Remove apostrophe from the phrase (important to do before s_regex regex)
        positions = []  # mark removal positions
        for i, char in enumerate(phrase):
            if char in self.apostrophes:
                positions.append(i)

        for pos in positions:
            # check if before or in entity
            for entity in entities:
                if pos < entity.get('end'):
                    entity['end'] -= 1
                if pos < entity.get('start'):
                    entity['start'] -= 1

        for entity in entities:
            for apostrophe in self.apostrophes:
                entity['value'] = entity['value'].replace(apostrophe, "")

        return entities

    def default_preprocessing(self, phrase: str = None, entities=None):

        if phrase is None:
            raise ValueError

        if entities:
            entities = self._handle_entities(phrase, entities)

        for apostrophe in self.apostrophes:
            phrase = phrase.replace(apostrophe, "")

        # lowercasing characters
        phrase = phrase.lower()
        if entities:
            for entity in entities:
                entity['value'] = entity['value'].lower()

        if self.remove_accent:
            phrase = unidecode(phrase)
            if entities:
                for entity in entities:
                    entity['value'] = unidecode(entity['value'])

        return phrase, entities

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
