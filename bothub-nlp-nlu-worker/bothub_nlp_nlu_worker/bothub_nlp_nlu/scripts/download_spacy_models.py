#!/usr/bin/env python
import os
import sys
import subprocess
import logging
import plac

from decouple import config
from spacy.cli import download
from spacy.cli import link
from spacy.util import get_package_path
from collections import OrderedDict


logger = logging.getLogger("download_spacy_models")


def cast_supported_languages(i):
    return OrderedDict([x.split(":", 1) if ":" in x else (x, x) for x in i.split("|")])


@plac.annotations(
    languages=plac.Annotation(help="Languages to download"),
    debug=plac.Annotation(help="Enable debug", kind="flag", abbrev="D"),
)
def download_spacy_models(languages=None, debug=False):
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
    plac.call(download_spacy_models, sys.argv[1:])
