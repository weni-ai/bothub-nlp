FROM ilha/scipy:python3.6-alpine3.7

ENV WORKDIR /home/app
WORKDIR $WORKDIR

RUN apk update && apk upgrade
RUN apk add alpine-sdk postgresql postgresql-dev libpng openblas-dev

COPY . .
RUN pip install --exists-action w -r requirements.txt
RUN python -m spacy download en
RUN python -m spacy download de
RUN python -m spacy download es
RUN python -m spacy download pt
RUN python -m spacy download fr
RUN python -m spacy download it
RUN python -m spacy download nl

RUN apk del alpine-sdk postgresql-dev openblas-dev

RUN chmod +x ./docker/entrypoint.sh
RUN chmod +x ./app/server.py
EXPOSE 8080
ENTRYPOINT $WORKDIR/docker/entrypoint.sh