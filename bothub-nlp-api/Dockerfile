FROM python:3.6-alpine

RUN apk update \
    && apk --virtual .build-dependencies add \
        alpine-sdk \
        git \
        python3-dev \
    && apk add postgresql-dev \
    && pip install pipenv psycopg2-binary

ENV WORKDIR /root/app

WORKDIR $WORKDIR

COPY bothub-nlp ../bothub-nlp
COPY bothub-nlp-celery ../bothub-nlp-celery
COPY bothub-nlp-api/Pipfile .
COPY bothub-nlp-api/Pipfile.lock .

RUN pipenv install --system --deploy \
    && apk del .build-dependencies \
    && rm -rf /var/cache/apk/*

COPY bothub-nlp-api .

ENTRYPOINT [ "python", "-m", "bothub_nlp_api" ]
