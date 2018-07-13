#!/bin/sh
if [[ ${DOWNLOADED_LANGUAGES} != ${SUPPORTED_LANGUAGES} ]]; then make download_supported_languages; fi
make start
