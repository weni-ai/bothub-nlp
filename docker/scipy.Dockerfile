FROM python:3.6-alpine3.7

RUN apk update && apk upgrade
RUN apk add alpine-sdk freetype-dev openblas-dev

RUN pip install numpy
RUN pip install scipy matplotlib ipython jupyter pandas sympy nose

RUN apk del alpine-sdk freetype-dev openblas-dev