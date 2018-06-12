ENV_DIR=./env/
SETTINGS_FILE=settings.ini
DJANGO_SETTINGS_MODULE=bothub.settings
EXTRA_MODELS_DIR=./spacy-lang-models/models/
SUPPORTED_LANGUAGES=en de es pt fr it nl

help:
	@cat Makefile-help.txt

init_envoriment:
	virtualenv -p python3.6 $(ENV_DIR);
	$(ENV_DIR)bin/pip install --upgrade pip
	make install_requirements

clone_spacy_lang_models:
	git clone https://github.com/push-flow/spacy-lang-models.git

check_envoriment:
	if [ ! -d "$(ENV_DIR)" ]; then make init_envoriment; fi
	if [ ! -d "$(EXTRA_MODELS_DIR)" ]; then make clone_spacy_lang_models; fi

install_requirements:
	make check_envoriment
	$(ENV_DIR)bin/pip install -r requirements.txt

lint:
	make check_envoriment
	$(ENV_DIR)bin/flake8

create_development_settings:
	echo "[settings]" > $(SETTINGS_FILE)
	echo "SECRET_KEY=SK" >> $(SETTINGS_FILE)
	echo "DEBUG=True" >> $(SETTINGS_FILE)

check_ready_for_development:
	make check_envoriment
	if [ ! -f "$(SETTINGS_FILE)" ]; then make create_development_settings; fi

migrate:
	make check_envoriment
	DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) $(ENV_DIR)bin/django-admin migrate

import_languages:
	make check_envoriment
	$(ENV_DIR)bin/python -m bothub-nlp import_langs -e=${EXTRA_MODELS_DIR} ${SUPPORTED_LANGUAGES}

test:
	make check_ready_for_development
	make migrate
	$(ENV_DIR)bin/coverage run -m unittest
	$(ENV_DIR)bin/coverage report -m

start:
	make check_ready_for_development
	make migrate
	$(ENV_DIR)bin/python -m app --service start_server 8001
