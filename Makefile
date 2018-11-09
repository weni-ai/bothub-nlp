ENVIRONMENT_VARS_FILE := .env
DJANGO_SETTINGS_MODULE := bothub.settings
IS_PRODUCTION ?= false
CHECK_ENVIRONMENT := true


# Commands

help:
	@cat Makefile-help.txt
	@exit 0

check_environment:
	@if [ ${CHECK_ENVIRONMENT} = true ]; then make _check_environment; fi

install_requirements:
	@if [ ${IS_PRODUCTION} = true ]; \
		then make install_production_requirements; \
		else make install_development_requirements; fi

lint:
	@make development_mode_guard
	@make check_environment
	@PIPENV_DONT_LOAD_ENV=1 pipenv run flake8
	@echo "${SUCCESS}✔${NC} The code is following the PEP8"

ifeq (test,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(RUN_ARGS):;@:)
endif

test:
	@make development_mode_guard
	@make check_environment
	@PIPENV_DONT_LOAD_ENV=1 SECRET_KEY=SK DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE}" pipenv run django-admin migrate
	@PIPENV_DONT_LOAD_ENV=1 SECRET_KEY=SK SUPPORTED_LANGUAGES="en|pt" SEND_EMAILS=false pipenv run coverage run -m unittest $(RUN_ARGS)
	@if [ ! $(RUN_ARGS) ]; then PIPENV_DONT_LOAD_ENV=1 pipenv run coverage report -m; fi;

migrate:
	@make check_environment
	@if [ ${IS_PRODUCTION} = true ]; \
		then DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE}" django-admin migrate; \
		else DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE}" pipenv run django-admin migrate; fi

download_supported_languages:
	@make check_environment
	@if [ ${IS_PRODUCTION} = true ]; \
		then python scripts/download_spacy_models.py; \
		else pipenv run python scripts/download_spacy_models.py; fi

import_ilha_spacy_langs:
	@make check_environment
	@if [ ${IS_PRODUCTION} = true ]; \
		then ./scripts/import_ilha_spacy_langs.sh; \
		else pipenv run ./scripts/import_ilha_spacy_langs.sh; fi

start:
	@make check_environment
	@make migrate CHECK_ENVIRONMENT=false
	@if [ ${IS_PRODUCTION} = true ]; \
		then python -m bothub_nlp.server; \
		else pipenv run python -m tornado.autoreload -m bothub_nlp.server; fi

start_celery_worker:
	@make check_environment
	@make migrate CHECK_ENVIRONMENT=false
	@if [ ${IS_PRODUCTION} = true ]; \
		then celery worker -A bothub_nlp.core.celery -l INFO; \
		else pipenv run celery worker -A bothub_nlp.core.celery -l INFO; \
	fi


# Utils

## Colors
SUCCESS = \033[0;32m
INFO = \033[0;36m
WARNING = \033[0;33m
DANGER = \033[0;31m
NC = \033[0m

create_environment_vars_file:
	@echo "SECRET_KEY=SK" > "${ENVIRONMENT_VARS_FILE}"
	@echo "DEBUG=true" >> "${ENVIRONMENT_VARS_FILE}"
	@echo "SUPPORTED_LANGUAGES=en|pt" >> "${ENVIRONMENT_VARS_FILE}"
	@echo "${SUCCESS}✔${NC} Settings file created"

install_development_requirements:
	@echo "${INFO}Installing development requirements...${NC}"
	@pipenv install --dev
	@echo "${SUCCESS}✔${NC} Development requirements installed"

install_production_requirements:
	@echo "${INFO}Installing production requirements...${NC}"
	@pipenv install --system -v
	@echo "${SUCCESS}✔${NC} Requirements installed"

development_mode_guard:
	@if [ ${IS_PRODUCTION} = true ]; then echo "${DANGER}Just run this command in development mode${NC}"; fi
	@if [ ${IS_PRODUCTION} = true ]; then exit 1; fi


# Checkers

_check_environment:
	@type pipenv || (echo "${DANGER}☓${NC} Install pipenv to continue..." && exit 1)
	@echo "${SUCCESS}✔${NC} pipenv installed"
	@if [ ! -f "${ENVIRONMENT_VARS_FILE}" ] && [ ${IS_PRODUCTION} = false ]; then make create_environment_vars_file; fi
	@make install_requirements
	@echo "${SUCCESS}✔${NC} Environment checked"