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

RUN chmod +x ./entrypoint.sh ./worker-on-demand-entrypoint.sh

ENTRYPOINT $WORKDIR/entrypoint.sh