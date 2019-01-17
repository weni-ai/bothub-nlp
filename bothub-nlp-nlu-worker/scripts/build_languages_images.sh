#!/bin/sh

LANGUAGES_LIST=$(echo $SUPPORTED_LANGUAGES | tr "|" "\n")

for language in $LANGUAGES_LIST
do
    language_split=$(echo $language | tr ":" " ")
    docker_tag=$(echo $language_split | head -n1 | awk '{print $1;}')
    BOTHUB_NLP_NLU_WORKER_DOCKER_IMAGE_TAG=$docker_tag docker-compose build --build-arg DOWNLOAD_SPACY_MODELS=${language} bothub-nlp-nlu-worker
done

if [ ${PUSH_IMAGE} = true ];
then
    for language in $LANGUAGES_LIST
    do
        language_split=$(echo $language | tr ":" " ")
        docker_tag=$(echo $language_split | head -n1 | awk '{print $1;}')
        docker push ${BOTHUB_NLP_NLU_WORKER_DOCKER_IMAGE_NAME}:$docker_tag
    done
fi
