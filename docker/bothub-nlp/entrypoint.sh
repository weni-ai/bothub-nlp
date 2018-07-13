#!/bin/sh
if [[ ${DOWNLOADED_LANGUAGES} != ${SUPPORTED_LANGUAGES} ]]; then make download_supported_languages; fi
make import_ilha_spacy_langs CHECK_ENVIRONMENT=false
make start CHECK_ENVIRONMENT=false
