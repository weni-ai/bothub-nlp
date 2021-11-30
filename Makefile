init_development_env:
	@echo "${INFO}Starting init environment...${NC}"
	@echo "BOTHUB_ENGINE_URL=http://localhost" >> .env
	@echo "BOTHUB_NLP_SERVICE_WORKER=True" >> .env
	@echo "BOTHUB_NLP_LANGUAGE_QUEUE=en" >> .env
	@echo "BOTHUB_LANGUAGE_MODEL=BERT" >> .env
	@echo "${SUCCESS}Finish...${NC}"

start_development:
	@echo "${INFO}Starting Build all project (Docker)...${NC}"
	@docker-compose build --build-arg DOWNLOAD_MODELS=en-BERT
	@docker-compose up -d
	@echo "${SUCCESS}Finish...${NC}"


install_development_requirements:
	@echo "${INFO}Installing development requirements...${NC}"
	@git clone --branch master --depth 1 --single-branch https://github.com/Ilhasoft/spacy-lang-models spacy-langs
	@python bothub/shared/utils/scripts/link_lang_spacy.py pt_br ./spacy-langs/pt_br/
	@python bothub/shared/utils/scripts/download_models.py en-BERT
	@echo "${SUCCESS}✔${NC} Development requirements installed"


start_celery:
	@python start_celery.py

# Utils

## Colors
SUCCESS = \033[0;32m
INFO = \033[0;36m
WARNING = \033[0;33m
DANGER = \033[0;31m
NC = \033[0m
