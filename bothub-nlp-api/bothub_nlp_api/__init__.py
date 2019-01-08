import os
import django
import logging


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bothub.settings')
django.setup()

logger = logging.getLogger('bothub_nlp_api')
