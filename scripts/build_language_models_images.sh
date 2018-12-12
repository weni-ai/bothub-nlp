#!/bin/sh

LANGUAGES_LIST=$(echo $SUPPORTED_LANGUAGES | tr "|" "\n")

for language in $LANGUAGES_LIST
do
    language_split=$(echo $language | tr ":" " ")
    docker_tag=$(echo $language_split | head -n1 | awk '{print $1;}')
    BOTHUB_NLP_WORKER_DOCKER_IMAGE_TAG=$docker_tag docker-compose build --build-arg DOWNLOAD_LANGUAGES_MODELS=${language} --build-arg BOTHUB_NLP_DOCKER_IMAGE_NAME=${BOTHUB_NLP_DOCKER_IMAGE_NAME} --build-arg BOTHUB_NLP_DOCKER_IMAGE_TAG=${BOTHUB_NLP_DOCKER_IMAGE_TAG} worker
    if [ ${PUSH_IMAGE} = true ];
    then
        docker push ${BOTHUB_NLP_WORKER_DOCKER_IMAGE_NAME}:$docker_tag
    fi
done
