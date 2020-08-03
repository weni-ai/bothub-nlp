#!/usr/bin/env python
import os
import sys
import subprocess
import logging
import plac
import requests

from decouple import config
from spacy.cli import download
from spacy.cli import link
from spacy.util import get_package_path
from collections import OrderedDict
from transformers.file_utils import TF2_WEIGHTS_NAME, WEIGHTS_NAME, hf_bucket_url
from bothub_nlp_rasa_utils.pipeline_components.registry import (
    model_weights_defaults,
    from_pt_dict,
    model_config_url,
)

logger = logging.getLogger("download_models")

lang_to_model = {
    "en": {"SPACY": "en_core_web_lg", "BERT": "bert_english"},
    "pt_br": {
        "SPACY": "pip+pt_nilc_word2vec_cbow_600:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/pt_nilc_word2vec_cbow_600-1.0.0.zip",
        "BERT": "bert_portuguese",
    },
    "de": {"SPACY": "de"},
    "es": {"SPACY": "es_core_news_md"},
    "pt": {"SPACY": "pt"},
    "fr": {"SPACY": "fr_core_news_md"},
    "it": {"SPACY": "it"},
    "nl": {"SPACY": "nl"},
    "id": {
        "SPACY": "pip+id_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/id_vectors_web_md-1.1.0.tar.gz"
    },
    "mn": {
        "SPACY": "pip+mn_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/mn_vectors_web_md-1.1.0.tar.gz"
    },
    "ar": {
        "SPACY": "pip+ar_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/ar_vectors_web_md-1.1.0.tar.gz"
    },
    "bn": {
        "SPACY": "pip+bn_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/bn_vectors_web_md-1.1.0.tar.gz"
    },
    "hi": {
        "SPACY": "pip+hi_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/hi_vectors_web_md-1.1.0.tar.gz"
    },
    "ru": {
        "SPACY": "pip+ru_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/ru_vectors_web_md-1.1.0.tar.gz"
    },
    "th": {
        "SPACY": "pip+th_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/th_vectors_web_md-1.1.0.tar.gz"
    },
    "fi": {
        "SPACY": "pip+fi_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/fi_vectors_web_md-1.1.0.tar.gz"
    },
    "ga": {
        "SPACY": "pip+ga_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/ga_vectors_web_md-1.1.0.tar.gz"
    },
    "he": {
        "SPACY": "pip+he_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/he_vectors_web_md-1.1.0.tar.gz"
    },
    "hr": {
        "SPACY": "pip+hr_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/hr_vectors_web_md-1.1.0.tar.gz"
    },
    "hu": {
        "SPACY": "pip+hu_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/hu_vectors_web_md-1.1.0.tar.gz"
    },
    "nb": {
        "SPACY": "pip+nb_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/nb_vectors_web_md-1.1.0.tar.gz"
    },
    "pl": {
        "SPACY": "pip+pl_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/pl_vectors_web_md-1.1.0.tar.gz"
    },
    "ro": {
        "SPACY": "pip+ro_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/ro_vectors_web_md-1.1.0.tar.gz"
    },
    "si": {
        "SPACY": "pip+si_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/si_vectors_web_md-1.1.0.tar.gz"
    },
    "sv": {
        "SPACY": "pip+sv_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/sv_vectors_web_md-1.1.0.tar.gz"
    },
    "te": {
        "SPACY": "pip+te_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/te_vectors_web_md-1.1.0.tar.gz"
    },
    "tr": {
        "SPACY": "pip+tr_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/tr_vectors_web_md-1.1.0.tar.gz"
    },
    "tt": {
        "SPACY": "pip+tt_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/tt_vectors_web_md-1.1.0.tar.gz"
    },
    "ha": {
        "SPACY": "pip+ha_vectors_web_md:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/ha_vectors_web_md-1.1.0.tar.gz"
    },
    "el": {
        "SPACY": "pip+el_bothub_sm:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/el_bothub_sm-1.0.0.zip"
    },
    "ka": {
        "SPACY": "pip+ka_bothub_sm:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/ka_bothub_sm-1.0.0.zip"
    },
    "sw": {
        "SPACY": "pip+sw_bothub_sm:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/sw_bothub_sm-1.0.0.zip"
    },
    "kk": {
        "SPACY": "pip+kk_bothub_sm:https://s3.amazonaws.com/bothub-models/spacy-2.1.9/kk_bothub_sm-1.0.0.zip"
    },
    "xx": {"SPACY": "xx"},
}


def download_file(url, file_name):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_name, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return file_name


def download_bert(model_name, model_dir):
    os.makedirs(model_dir, exist_ok=True)
    from_pt = from_pt_dict.get(model_name, False)
    model_url = hf_bucket_url(
        model_weights_defaults.get(model_name),
        filename=(WEIGHTS_NAME if from_pt else TF2_WEIGHTS_NAME),
    )

    config_url = model_config_url.get(model_name)
    logger.info("downloading bert")
    model_name = "pytorch_model.bin" if from_pt else "tf_model.h5"
    download_file(model_url, os.path.join(model_dir, model_name))
    download_file(config_url, os.path.join(model_dir, "config.json"))
    logger.info("finished downloading bert")


def cast_supported_languages(languages):
    return languages.split("|")


@plac.annotations(
    languages=plac.Annotation(help="Languages to download"),
    debug=plac.Annotation(help="Enable debug", kind="flag", abbrev="D"),
)
def download_models(languages=None, debug=False):
    logging.basicConfig(
        format="%(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG if debug else logging.INFO,
    )

    if not languages:
        languages = config("SUPPORTED_LANGUAGES", default="", cast=str)
    languages = cast_supported_languages(languages)

    for lang in languages:
        lang = lang.split("-")

        lang_slug = lang[0]
        model = lang[1] if len(lang) > 1 else None
        value = lang_to_model.get(lang_slug, {}).get(model, None)

        if model == "SPACY":
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
            download_bert(value, model_dir="bothub_nlp_nlu_worker/model")


if __name__ == "__main__":
    plac.call(download_models, sys.argv[1:])
