import logging

from .utils import UpdateInterpreters
from .utils import SpacyNLPLanguageManager


logger = logging.getLogger('bothub_nlp.core')

updateInterpreters = UpdateInterpreters()
spacy_nlp_languages = SpacyNLPLanguageManager()
