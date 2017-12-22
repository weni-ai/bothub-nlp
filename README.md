# Bothub Demo
[![Coverage Status](https://coveralls.io/repos/github/push-flow/bothub-nlp/badge.svg?branch=master)](https://coveralls.io/github/push-flow/bothub-nlp?branch=master) [![Build Status](https://travis-ci.org/push-flow/bothub-nlp.svg?branch=master)](https://travis-ci.org/push-flow/bothub-nlp)

 ##### How to run 
 #
    docker build -t bothub-nlp . 
 #
    docker run -e APP_REPOSITORY_URL=https://github.com/push-flow/bothub-nlp.git \
    -e APP_REPOSITORY_BRANCH=master \
    -e BOTHUB_POSTGRES_USER=postgres \
    -e BOTHUB_POSTGRES_PASSWORD=postgres \
    -e BOTHUB_POSTGRES_DB=bothub \
    -e BOTHUB_POSTGRES=127.0.0.1 \
    -e BOTHUB_POSTGRES_PORT=5432 \
    -e BOTHUB_REDIS=127.0.0.1 \
    -e BOTHUB_REDIS_PORT=6379 \
    -e BOTHUB_DEBUG=True \
    -e BOTHUB_REDIS_DB=2 -p "8000:80" \
    bothub-nlp
