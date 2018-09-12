# Bothub NLP

[![Coverage Status](https://coveralls.io/repos/github/Ilhasoft/bothub-nlp/badge.svg?branch=master)](https://coveralls.io/github/Ilhasoft/bothub-nlp?branch=master) [![Build Status](https://travis-ci.org/Ilhasoft/bothub-nlp.svg?branch=master)](https://travis-ci.org/Ilhasoft/bothub-nlp) [![Python Version](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/) [![License GPL-3.0](https://img.shields.io/badge/license-%20AGPL--3.0-yellow.svg)](https://github.com/Ilhasoft/bothub-nlp/blob/refactor/LICENSE)


## Development

Use ```make``` commands to ```check_environment```, ```install_requirements```, ```lint```, ```test```, ```migrate``` and ```start```.

| Command | Description |
|--|--|
| make help | Show make commands help
| make check_environment | Check if all dependencies was installed
| make install_requirements | Install pip dependencies
| make lint | Show lint warnings and errors
| make test | Run unit tests and show coverage report
| make migrate | Update DB shema, apply migrations
| make download_supported_languages | Download and link all supported languages
| make import_ilha_spacy_langs | Import languages from Ilhasoft spaCy repository
| make start | Start web server

## Production

Docker images available in [Bothub NLP's Docker Hub repository](https://hub.docker.com/r/ilha/bothub-nlp/).


## Environment Variables

| Variable | Type | Default | Description |
|--|--|--|--|
| IS_PRODUCTION | ```boolean``` | ```false``` | Use ```true``` to force pipenv use system envoriment.
| DEVELOPMENT_MODE | ```boolean``` | ```DEBUG``` value | When ```true```, tornado's autoreload is enabled.
| PORT | ```int``` | ```2657``` | Port to run web server.
| SUPPORTED_LANGUAGES | ```string``` | In development mode: ```en|pt``` | Set supported languages. Separe languages using ```|```. You can set location follow the format: [LANGUAGE_CODE]:[LANGUAGE_LOCATION].
| LOGGER_FORMAT | ```string``` | ```%(asctime)s - %(name)s - %(levelname)s - %(message)s``` | Logger format.
| LOGGER_LEVEL | ```int``` | DEBUG = ```10`` | Logger level, use logging (Python Package) pattern.
| NLP_SENTRY_CLIENT | ```string``` | empty | Sentry Client URL

Check another valid environment variables in [Bothub repository](https://github.com/Ilhasoft/bothub-engine).
