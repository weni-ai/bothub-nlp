import logging
from bothub.shared.utils.preprocessing.preprocessing_english import PreprocessingEnglish
from bothub.shared.utils.preprocessing.preprocessing_portuguese import PreprocessingPortuguese
from bothub.shared.utils.preprocessing.preprocessing_spanish import PreprocessingSpanish
from bothub.shared.utils.preprocessing.preprocessing_base import PreprocessingBase

logger = logging.getLogger(__name__)


class PreprocessingFactory(object):

    def __init__(self, language=None, remove_accent=True):
        self.language = language
        self.remove_accent = remove_accent

    def factory(self):
        """
        Implements Factory Method
        :return: Preprocessing Class respective to its language
        """
        try:
            if self.language == "en":
                return PreprocessingEnglish(self.remove_accent)
            elif self.language == "pt_br":
                return PreprocessingPortuguese(self.remove_accent)
            elif self.language == "es":
                return PreprocessingSpanish(self.remove_accent)
            else:
                return PreprocessingBase(self.remove_accent)

        except AssertionError as e:
            logger.exception(e)

        return None
