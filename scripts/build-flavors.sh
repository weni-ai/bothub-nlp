#!/bin/sh

# latest
docker-compose -f docker/docker-compose.yml build bothub-nlp

# all languages
DOCKER_IMAGE_FLAVOR="-all" DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD="en|de|es|pt|fr|it|nl" docker-compose -f docker/docker-compose.yml build bothub-nlp

# all languages using vectors
DOCKER_IMAGE_FLAVOR="-all-vectorized" DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD="en:en_core_web_lg|de|es:es_core_news_md|pt|fr:fr_core_news_md|it|nl" docker-compose -f docker/docker-compose.yml build bothub-nlp

# all languages using vectors + pt_br
DOCKER_IMAGE_FLAVOR="-full" DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD="en:en_core_web_lg|de|es:es_core_news_md|pt|fr:fr_core_news_md|it|nl|pt_br:pip+pt-br-vectors-web-lg:https://s3.amazonaws.com/bothub-models/spacy/pt_br_vectors_web_lg-1.0.0.tar.gz" docker-compose -f docker/docker-compose.yml build bothub-nlp
