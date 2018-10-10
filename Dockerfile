FROM python:3.6.6

ENV WORKDIR /home/app
ENV IS_PRODUCTION true
ENV PORT 2657

WORKDIR $WORKDIR

RUN pip install pipenv
RUN pip install psycopg2-binary

COPY Pipfile .
COPY Pipfile.lock .
COPY Makefile .

RUN make -s check_environment

COPY . .

ARG DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD
RUN if [ ${DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD} ]; \
        then python scripts/download_spacy_models.py ${DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD}; \
    fi
ENV DOWNLOADED_LANGUAGES ${DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD}

RUN make -s import_ilha_spacy_langs CHECK_ENVIRONMENT=false

RUN chmod +x ./entrypoint.sh
ENTRYPOINT $WORKDIR/entrypoint.sh