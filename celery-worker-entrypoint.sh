#!/bin/bash

if [ "$DOWNLOADED_LANGUAGES" != "$SUPPORTED_LANGUAGES" ]
then
    python scripts/download_spacy_models.py
fi

celery worker -A bothub_nlp.core.celery -c 1 -l INFO $@
