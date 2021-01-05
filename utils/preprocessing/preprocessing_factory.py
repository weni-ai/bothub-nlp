from bothub_nlp_rasa_utils import logger

from .preprocessing_base import PreprocessingBase
from .preprocessing_english import PreprocessingEnglish
from .preprocessing_portuguese import PreprocessingPortuguese


class PreprocessingFactory:
    """The Factory Class"""

    @staticmethod
    def get_preprocess(language: str = None):
        
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
