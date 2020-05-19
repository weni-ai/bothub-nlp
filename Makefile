lint:
	@echo "${INFO}Linting...${NC}"
	@export PIPENV_DONT_LOAD_ENV=1
	@cd bothub-nlp-api \
		&& PIPENV_DONT_LOAD_ENV=1 pipenv run lint \
		&& echo "${SUCCESS}✔${NC} bothub-nlp-api" || echo "${DANGER}✖${NC} bothub-nlp-api"
	@cd bothub-nlp-nlu-worker \
		&& PIPENV_DONT_LOAD_ENV=1 pipenv run lint \
		&& echo "${SUCCESS}✔${NC} bothub-nlp-nlu-worker" || echo "${DANGER}✖${NC} bothub-nlp-nlu-worker"
	@cd bothub-nlp-nlu-worker-on-demand \
		&& PIPENV_DONT_LOAD_ENV=1 pipenv run lint \
		&& echo "${SUCCESS}✔${NC} bothub-nlp-nlu-worker-on-demand" || echo "${DANGER}✖${NC} bothub-nlp-nlu-worker-on-demand"

init_env:
	@echo "${INFO}Starting init environment...${NC}"
	@echo "SUPPORTED_LANGUAGES=en:en_core_web_md" >> .env
	@echo "BOTHUB_ENGINE_URL=https://api.bothub.it" >> .env
	@echo "ENGINE_PORT=8000" >> .env
	@echo "${SUCCESS}Finish...${NC}"

start_development:
	@echo "${INFO}Starting Build all project (Docker)...${NC}"
	@docker-compose build --build-arg DOWNLOAD_SPACY_MODELS=en:en_core_web_md
	@docker-compose up -d
	@echo "${SUCCESS}Finish...${NC}"


install_development_requirements:
	@echo "${INFO}Installing development requirements...${NC}"
	@git clone --branch master --depth 1 --single-branch https://github.com/Ilhasoft/spacy-lang-models spacy-langs
	@python scripts/link_lang_spacy.py pt_br ./spacy-langs/pt_br/
	@python scripts/link_lang_spacy.py mn ./spacy-langs/mn/
	@python scripts/link_lang_spacy.py ha ./spacy-langs/ha/
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
