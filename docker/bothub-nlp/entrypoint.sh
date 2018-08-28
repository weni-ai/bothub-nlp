#!/bin/sh

if [ "$DOWNLOADED_LANGUAGES" != "$SUPPORTED_LANGUAGES" ]; \
    then python scripts/download_spacy_models.py;
fi

python -m bothub_nlp.server
