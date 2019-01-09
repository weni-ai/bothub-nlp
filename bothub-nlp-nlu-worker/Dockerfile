FROM ubuntu:xenial

ENV WORKDIR /home/root/app
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

WORKDIR $WORKDIR

COPY bothub-nlp-nlu-worker/Pipfile .
COPY bothub-nlp-nlu-worker/Pipfile.lock .

RUN apt-get update
RUN apt-get install -y software-properties-common git curl build-essential
RUN add-apt-repository ppa:fkrull/deadsnakes && apt-get update
RUN apt-get install -y python3.6 python3.6-dev
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.6 get-pip.py
RUN pip install pipenv psycopg2-binary redis

COPY bothub-nlp ../bothub-nlp
COPY bothub-nlp-celery ../bothub-nlp-celery
COPY bothub-nlp-nlu ../bothub-nlp-nlu

RUN pipenv install --deploy --system
RUN rm -rf /var/lib/apt/lists/*

COPY bothub-nlp-nlu-worker .

ARG DOWNLOAD_SPACY_MODELS

RUN if [ ${DOWNLOAD_SPACY_MODELS} ]; then \
        python3.6 ./scripts/download_spacy_models.py ${DOWNLOAD_SPACY_MODELS}; \
    fi

ENTRYPOINT [ "celery", "worker", "-A", "bothub_nlp_nlu_worker.celery_app" ]
