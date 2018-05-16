ENV_DIR=./env/
SETTINGS_FILE=settings.ini
DJANGO_SETTINGS_MODULE=bothub.settings

help:
	@cat Makefile-help.txt

init_envoriment:
	virtualenv -p python3.6 $(ENV_DIR);
	$(ENV_DIR)bin/pip install --upgrade pip
	make install_requirements

check_envoriment:
	if [ ! -d "$(ENV_DIR)" ]; then make init_envoriment; fi

install_requirements:
	make check_envoriment
	$(ENV_DIR)bin/pip install -r requirements.txt

update_requirements:
	make check_envoriment
	$(ENV_DIR)bin/pip freeze > requirements.txt

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

install_languages:
	make check_envoriment
	$(ENV_DIR)bin/python -m spacy download en
	$(ENV_DIR)bin/python -m spacy download de
	$(ENV_DIR)bin/python -m spacy download es
	$(ENV_DIR)bin/python -m spacy download pt
	$(ENV_DIR)bin/python -m spacy download fr
	$(ENV_DIR)bin/python -m spacy download it
	$(ENV_DIR)bin/python -m spacy download nl

test:
	make check_ready_for_development
	make migrate
	$(ENV_DIR)bin/coverage run -m unittest
	$(ENV_DIR)bin/coverage report -m

start:
	make check_ready_for_development
	make migrate
	$(ENV_DIR)bin/python -m app --service start_server 8001
