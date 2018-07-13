FROM ilha/scipy:python3.6-alpine3.7

ENV WORKDIR /home/app
ENV IS_PRODUCTION true
ENV PORT 2657

WORKDIR $WORKDIR

RUN apk update && apk upgrade
RUN apk add alpine-sdk postgresql-dev libpng openblas-dev freetype-dev libpng-dev

RUN pip install pipenv
RUN pip install psycopg2-binary

COPY Makefile .
COPY Pipfile .
COPY Pipfile.lock .

RUN make check_environment

COPY . .

ARG DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD
RUN if [[ ${DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD} ]]; then python download_spacy_models.py ${DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD}; fi

RUN chmod +x ./docker/bothub-nlp/entrypoint.sh
EXPOSE 2657
ENTRYPOINT $WORKDIR/docker/bothub-nlp/entrypoint.sh