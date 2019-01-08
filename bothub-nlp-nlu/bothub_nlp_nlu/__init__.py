import os
import django
import logging

from .utils import UpdateInterpreters
from .utils import SpacyNLPLanguageManager


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bothub.settings')
django.setup()

logger = logging.getLogger('bothub_nlp_nlu')

updateInterpreters = UpdateInterpreters()
spacy_nlp_languages = SpacyNLPLanguageManager()
