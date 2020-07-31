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
                                                model_config_url
                                            )

logger = logging.getLogger("download_models")


def download_file(url, file_name):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_name, 'wb') as f:
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
    logger.info('downloading bert')
    model_name = 'pytorch_model.bin' if from_pt else 'tf_model.h5'
    download_file(model_url, os.path.join(model_dir, model_name))
    download_file(config_url, os.path.join(model_dir, 'config.json'))
    logger.info('finished downloading bert')


def cast_supported_languages(i):
    return OrderedDict([x.split(":", 1) if ":" in x else (x, x) for x in i.split("|")])


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

    logger.info("Importing langs: {}".format(", ".join(languages.keys())))

    for lang, value in languages.items():
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
                logger.debug("linking: {} to {}".format(model_name, lang))
                package_path = get_package_path(model_name)
                link(model_name, lang, force=True, model_path=package_path)
            else:
                raise Exception("Error to download {}".format(lang))
        elif value.startswith("bert+"):
            model_name = value.split('+', 1)[1]
            download_bert(model_name, model_dir='model')
        elif lang != value:
            logger.debug("downloading {}".format(value))
            download(value)
            logger.debug("linking: {} to {}".format(value, lang))
            package_path = get_package_path(value)
            link(value, lang, force=True, model_path=package_path)
        else:
            logger.debug("downloading {}".format(value))
            download(value)


if __name__ == "__main__":
    plac.call(download_models, sys.argv[1:])
