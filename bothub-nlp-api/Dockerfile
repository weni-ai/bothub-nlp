FROM python:3.6-alpine

ENV WORKDIR /root/app
ENV BOTHUB_NLP_API_PORT 2657

WORKDIR $WORKDIR

COPY bothub-nlp-api/Pipfile .
COPY bothub-nlp-api/Pipfile.lock .

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

COPY bothub-nlp-api .

ENTRYPOINT [ "python", "-m", "bothub_nlp_api" ]
