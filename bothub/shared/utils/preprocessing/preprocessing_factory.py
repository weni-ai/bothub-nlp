import logging
from bothub.shared.utils.preprocessing.preprocessing_english import PreprocessingEnglish
from bothub.shared.utils.preprocessing.preprocessing_portuguese import PreprocessingPortuguese
from bothub.shared.utils.preprocessing.preprocessing_base import PreprocessingBase

logger = logging.getLogger(__name__)


class PreprocessingFactory(object):

    @staticmethod
    def factory(language: str = None):
        """
        Implements Factory Method
        :param language: Language
        :return: Preprocessing Class respective to its language
        """
        try:
            if language == "en":
                return PreprocessingEnglish()
            elif language == "pt_br":
                return PreprocessingPortuguese()
            else:
                return PreprocessingBase()

        except AssertionError as e:
            logger.exception(e)

        return None
