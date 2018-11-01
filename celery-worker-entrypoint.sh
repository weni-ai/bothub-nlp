#!/bin/bash

if [ "$DOWNLOADED_LANGUAGES" != "$SUPPORTED_LANGUAGES" ]
then
    python scripts/download_spacy_models.py
fi

make -s start_celery_worker CHECK_ENVIRONMENT=false
