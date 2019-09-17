
# Commands

install_development_requirements:
	@echo "${INFO}Installing development requirements...${NC}"
	@echo "SERVER_PORT=2657" >> .env
	@echo "BOTHUB_ENGINE_URL=http://localhost:8000" >> .env
	@cp -a ../bothub-nlp-nlu-worker/bothub_nlp_nlu_worker/bothub_nlp_celery/* bothub_nlp_api/celerytasks/
	@echo "${SUCCESS}✔${NC} Development requirements installed"


# Utils

## Colors
SUCCESS = \033[0;32m
INFO = \033[0;36m
WARNING = \033[0;33m
DANGER = \033[0;31m
NC = \033[0m

