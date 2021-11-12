"""
Script to download language models on demand
Usage example:
!python download_models.py pt_br-BERT
"""

# !/usr/bin/env python
import os
import sys
import subprocess
import logging
import plac
import requests
import zipfile

from decouple import config
from spacy.cli import download
from spacy.cli import link
from spacy.util import get_package_path

sys.path.insert(
    1, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
)

from bothub.shared.utils.rasa_components.registry import model_url

logger = logging.getLogger(__name__)

lang_to_model = {
    "en": {"SPACY": "en_core_web_lg", "BERT": "bert_english"},
    "pt_br": {
        "SPACY": "pip+pt_nilc_word2vec_cbow_600:https://bothub-nlp-models.s3.amazonaws.com/pt_br-spacy/pt_nilc_word2vec_cbow_600-1.0.0.tar.gz",
        "SPACY_SUGGESTION": "pip+pt_nilc_wang2vec_cbow_300:https://bothub-nlp-models.s3.amazonaws.com/pt_br-spacy/pt_nilc_wang2vec_cbow_300-1.0.0.tar.gz",
        "BERT": "bert_portuguese",
    },
    "es": {"SPACY": "es_core_news_md"},
    "fr": {"SPACY": "fr_core_news_md"},
    "ru": {
        "SPACY": "pip+ru_vectors_web_md:https://bothub-nlp-models.s3.amazonaws.com/ru-spacy/ru_vectors_web_md-1.1.0.tar.gz"
    },
    "xx": {"BERT": "bert_multilang"},
}


def download_file(url, file_name):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_name, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return file_name


def download_bert(model_name):
    model_dir = model_name
    os.makedirs(model_dir, exist_ok=True)

    zipped_file_name = "temp.zip"
    url = model_url.get(model_name)
    logger.info(f"downloading {model_name} . . .")
    download_file(url, zipped_file_name)

    logger.info(f"extracting {model_name} . . .")
    with zipfile.ZipFile(zipped_file_name, 'r') as zip_ref:
        zip_ref.extractall(model_dir)
    os.remove(zipped_file_name)


def cast_supported_languages(languages):
    return languages.split("|")


@plac.annotations(
    languages=plac.Annotation(help="Languages to download"),
    debug=plac.Annotation(help="Enable debug", kind="flag", abbrev="D"),
)
def download_models(languages="", debug=False):
    logging.basicConfig(
        format="%(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG if debug else logging.INFO,
    )

    languages = cast_supported_languages(languages)

    for lang in languages:
        lang = lang.split("-")

        lang_slug = lang[0]
        model = lang[1] if len(lang) > 1 else None

        if not model or model == "NONE":
            continue

        value = lang_to_model.get(lang_slug, {}).get(model, None)
        if model.startswith("SPACY"):
            if value.startswith("pip+"):
                model_name, pip_package = value[4:].split(":", 1)
                logger.debug("model name: {}".format(model_name))
                logger.debug("pip package: {}".format(pip_package))
                cmd = [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--no-deps",
                    "--no-cache-dir",
                    pip_package,
                ]
                logger.debug(" ".join(cmd))
                if subprocess.call(cmd, env=os.environ.copy()) == 0:
                    logger.debug("linking: {} to {}".format(model_name, lang_slug))
                    package_path = get_package_path(model_name)
                    link(model_name, lang_slug, force=True, model_path=package_path)
                else:
                    raise Exception("Error to download {}".format(lang_slug))
            elif lang_slug != value:
                logger.debug("downloading {}".format(value))
                download(value)
                logger.debug("linking: {} to {}".format(value, lang_slug))
                package_path = get_package_path(value)
                link(value, lang_slug, force=True, model_path=package_path)
            else:
                logger.debug("downloading {}".format(value))
                download(value)
        elif model == "BERT":
            download_bert(value)


if __name__ == "__main__":
    plac.call(download_models, sys.argv[1:])
