#!/bin/sh
mkdir /home/extra-models/
make clone_extra_language_models_repository EXTRA_LANGUAGE_MODELS_REPOSITORY_DIR=/home/extra-models/
make import_languages
make start
