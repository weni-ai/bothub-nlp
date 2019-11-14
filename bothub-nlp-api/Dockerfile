FROM python:3.6-alpine

ENV WORKDIR /root/app
ENV BOTHUB_NLP_API_PORT 2657

WORKDIR $WORKDIR

COPY bothub-nlp-api .

RUN apk update \
    && apk add --virtual .build-dependencies --no-cache \
        alpine-sdk \
        libc-dev \
        git \
        python3-dev \
    && apk add --no-cache postgresql-dev \
    && pip install pipenv psycopg2-binary redis \
    && pipenv install --system --deploy \
    && apk del .build-dependencies \
    && rm -rf /var/cache/apk/*

RUN chmod +x ./entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]