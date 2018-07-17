FROM python:3.6-alpine3.7

RUN apk update && apk upgrade
RUN apk add alpine-sdk freetype-dev openblas-dev

RUN pip install numpy==1.14.5
RUN pip install scipy==1.1.0

RUN apk del alpine-sdk freetype-dev openblas-dev