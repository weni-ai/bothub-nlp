import os
import sys
import subprocess

from spacy.cli import download
from spacy.cli import link
from bothub_nlp import settings

from . import logger


def download_supported_languages():
    logger.info('Importing langs: {}'.format(
        ', '.join(settings.SUPPORTED_LANGUAGES.keys())))
    for lang, value in settings.SUPPORTED_LANGUAGES.items():
        if value.startswith('pip+'):
            model_name, pip_package = value[4:].split(':', 1)
            logger.debug('model name: {}'.format(model_name))
            logger.debug('pip package: {}'.format(pip_package))
            cmd = [
                sys.executable,
                '-m',
                'pip',
                'install',
                '--no-deps',
                pip_package,
            ]
            logger.debug(' '.join(cmd))
            if subprocess.call(cmd, env=os.environ.copy()) is 0:
                logger.debug('linking: {} to {}'.format(model_name, lang))
                link(model_name, lang, force=True)
            else:
                raise Exception('Error to download {}'.format(lang))
        elif lang is not value:
            logger.debug('downloading {}'.format(value))
            download(value)
            logger.debug('linking: {} to {}'.format(value, lang))
            link(value, lang)
        else:
            logger.debug('downloading {}'.format(value))
            download(value)
