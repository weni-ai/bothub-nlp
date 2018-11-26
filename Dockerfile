FROM python:3.6-stretch as base

## builder
FROM base as builder

RUN pip install --target=/tmp/site-packages \
        pipenv \
        psycopg2-binary \
        tensorflow==1.12.0 \
        scikit-learn==0.20.1 \
        sklearn-crfsuite==0.3.6


## building
FROM base

ENV PATH="/usr/local/lib/python3.6/site-packages/bin:${PATH}"
ENV WORKDIR /root
ENV IS_PRODUCTION true
ENV PORT 2657

WORKDIR $WORKDIR

COPY --from=builder /tmp/site-packages /usr/local/lib/python3.6/site-packages

COPY Pipfile .
COPY Pipfile.lock .
COPY Makefile .

RUN make -s check_environment

COPY . .

RUN make -s import_ilha_spacy_langs CHECK_ENVIRONMENT=false

ARG DOWNLOAD_LANGUAGES_MODELS
RUN if [ ${DOWNLOAD_LANGUAGES_MODELS} ]; \
        then python scripts/download_spacy_models.py ${DOWNLOAD_LANGUAGES_MODELS}; \
    fi
ENV DOWNLOADED_LANGUAGES_MODELS ${DOWNLOAD_LANGUAGES_MODELS}

RUN chmod +x ./entrypoint.sh ./celery-worker-entrypoint.sh ./worker-on-demand-entrypoint.sh
ENTRYPOINT $WORKDIR/entrypoint.sh