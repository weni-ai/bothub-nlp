#!/bin/sh

if [ "$DOWNLOADED_LANGUAGES" != "$SUPPORTED_LANGUAGES" ]
then
    then python scripts/download_spacy_models.py
fi

make start CHECK_ENVIRONMENT=false
