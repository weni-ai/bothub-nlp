# bothub NLP

[![Coverage Status](https://coveralls.io/repos/github/push-flow/bothub-nlp/badge.svg?branch=master)](https://coveralls.io/github/push-flow/bothub-nlp?branch=master) [![Build Status](https://travis-ci.org/push-flow/bothub-nlp.svg?branch=master)](https://travis-ci.org/push-flow/bothub-nlp) [![Python Version](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/) [![License GPL-3.0](https://img.shields.io/badge/license-%20GPL--3.0-yellow.svg)](https://github.com/push-flow/bothub/blob/master/LICENSE)


## Development

Use ```make``` commands to ```check_environment```, ```install_requirements```, ```lint```, ```test```, ```migrate```, ```import_languages``` and ```start```.

| Command | Description |
|--|--|
| make help | Show make commands help
| make check_environment | Check if all dependencies was installed
| make install_requirements | Install pip dependencies
| make lint | Show lint warnings and errors
| make test | Run unit tests and show coverage report
| make migrate | Update DB shema, apply migrations
| make import_languages [languages] | Import languages to Spacy
| make start | Start web server

## Production

Docker images available in [Bothub's Docker Hub repository](https://hub.docker.com/r/ilha/bothub/).


## Environment Variables

| Variable | Type | Default | Description |
|--|--|--|--|
| IS_PRODUCTION | ```boolean``` | ```false``` | Use ```true``` to force pipenv use system envoriment
| PORT | ```int``` | ```8001``` | Port to run web server
| SUPPORTED_LANGUAGES | ```list``` | In development mode: ```en de es pt fr it nl``` | Supported languages, common environment variable to bothub, bothub-webapp and bothub-nlp

Check another valid environment variables in [Bothub repository](https://github.com/push-flow/bothub/).
