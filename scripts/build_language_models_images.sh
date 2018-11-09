#!/bin/sh

LANGUAGES_LIST=$(echo $SUPPORTED_LANGUAGES | tr "|" "\n")

for language in $LANGUAGES_LIST
do
    language_split=$(echo $language | tr ":" " ")
    BOTHUB_NLP_DOCKER_IMAGE_TAG=language-$(echo $language_split | head -n1 | awk '{print $1;}') docker-compose build --build-arg DOWNLOAD_LANGUAGES_MODELS=${language} bothub-nlp
done
