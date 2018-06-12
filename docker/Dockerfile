FROM ilha/scipy:python3.6-alpine3.7

ENV WORKDIR /home/app
ENV EXTRA_MODELS_DIR /home/extra-models
WORKDIR $WORKDIR

RUN apk update && apk upgrade
RUN apk add alpine-sdk postgresql-dev libpng openblas-dev

RUN pip install cython==0.27.3 cymem==1.31.2 preshed==1.0.0 murmurhash==0.28.0 thinc==6.10.2

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x ./docker/entrypoint.sh
RUN chmod +x ./app/server.py
RUN mkdir "${EXTRA_MODELS_DIR}"
RUN git clone "${SPACY_LANG_MODELS_REPOSITORY}" "${EXTRA_MODELS_DIR}"
EXPOSE 8080
ENTRYPOINT $WORKDIR/docker/entrypoint.sh