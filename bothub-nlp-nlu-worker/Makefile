
# Commands

install_development_requirements:
	@echo "${INFO}Installing development requirements...${NC}"
	@git clone --branch master --depth 1 --single-branch https://github.com/Ilhasoft/spacy-lang-models spacy-langs
	@python scripts/link_lang_spacy.py pt_br ./spacy-langs/pt_br/
	@python scripts/link_lang_spacy.py mn ./spacy-langs/mn/
	@python bothub_nlp_nlu_worker/bothub_nlp_nlu/scripts/download_spacy_models.py en:en_core_web_md
	@echo "${SUCCESS}✔${NC} Development requirements installed"


start_celery:
	@celery worker --autoscale 50,10 -O fair --workdir bothub_nlp_nlu_worker -A celery_app -c 1 -l INFO -E -Q en



# Utils

## Colors
SUCCESS = \033[0;32m
INFO = \033[0;36m
WARNING = \033[0;33m
DANGER = \033[0;31m
NC = \033[0m

