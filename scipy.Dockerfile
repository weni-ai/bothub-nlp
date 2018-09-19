FROM python:3.6-alpine3.7

RUN apk update && apk upgrade && \
    apk add alpine-sdk freetype-dev openblas-dev && \
    pip install numpy==1.14.5 && \
    pip install scipy==1.1.0 && \
    apk del alpine-sdk freetype-dev openblas-dev