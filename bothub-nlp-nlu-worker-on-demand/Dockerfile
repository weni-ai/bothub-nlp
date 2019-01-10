FROM python:3.6-alpine

ENV WORKDIR /root/app
ENV BOTHUB_NLP_WORKER_ON_DEMAND_API_PORT 2658

WORKDIR $WORKDIR

COPY bothub-nlp ../bothub-nlp
COPY bothub-nlp-celery ../bothub-nlp-celery
COPY bothub-nlp-nlu-worker-on-demand/Pipfile .
COPY bothub-nlp-nlu-worker-on-demand/Pipfile.lock .

RUN apk update \
    && apk add --virtual .build-dependencies --no-cache \
        alpine-sdk \
        git \
        python3-dev \
    && apk add --no-cache postgresql-dev \
    && pip install pipenv psycopg2-binary redis \
    && pipenv install --system --deploy \
    && apk del .build-dependencies \
    && rm -rf /var/cache/apk/*

COPY bothub-nlp-nlu-worker-on-demand .

ENTRYPOINT [ "python", "-m", "bothub_nlp_nlu_worker_on_demand" ]
