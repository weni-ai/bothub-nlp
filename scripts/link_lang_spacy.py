#!/usr/bin/env python
import os
import sys
import plac
import importlib

from pathlib import Path
from spacy.util import get_package_path
from spacy.compat import symlink_to


@plac.annotations(
    lang=plac.Annotation(help='Language code'),
    lang_path=plac.Annotation(help='Language path'))
def link_lang_spacy(lang, lang_path):
    origin_path = os.path.join(get_package_path('spacy'), 'lang', lang)
    try:
        symlink_to(
            Path(origin_path),
            os.path.abspath(lang_path))
        try:
            importlib.import_module('spacy.lang.{}'.format(lang))
            print('link created')
        except Exception as e:
            print('link not created')
            raise e
    except Exception as e:
        print('error to create link to {} from {}'.format(lang, lang_path))
        raise e


if __name__ == '__main__':
    plac.call(link_lang_spacy, sys.argv[1:])
