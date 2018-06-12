#!/bin/sh
python -m bothub-nlp import_langs -e=${EXTRA_MODELS_DIR} ${SUPPORTED_LANGUAGES}
python -m app --service=start_server 8080
