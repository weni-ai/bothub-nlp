lint:
	@echo "${INFO}Linting...${NC}"
	@export PIPENV_DONT_LOAD_ENV=1
	@cd bothub-nlp \
		&& PIPENV_DONT_LOAD_ENV=1 pipenv run lint \
		&& echo "${SUCCESS}✔${NC} bothub-nlp" || echo "${DANGER}✖${NC} bothub-nlp"
	@cd bothub-nlp-api \
		&& PIPENV_DONT_LOAD_ENV=1 pipenv run lint \
		&& echo "${SUCCESS}✔${NC} bothub-nlp-api" || echo "${DANGER}✖${NC} bothub-nlp-api"
	@cd bothub-nlp-celery \
		&& PIPENV_DONT_LOAD_ENV=1 pipenv run lint \
		&& echo "${SUCCESS}✔${NC} bothub-nlp-celery" || echo "${DANGER}✖${NC} bothub-nlp-celery"
	@cd bothub-nlp-nlu \
		&& PIPENV_DONT_LOAD_ENV=1 pipenv run lint \
		&& echo "${SUCCESS}✔${NC} bothub-nlp-nlu" || echo "${DANGER}✖${NC} bothub-nlp-nlu"
	@cd bothub-nlp-nlu-worker \
		&& PIPENV_DONT_LOAD_ENV=1 pipenv run lint \
		&& echo "${SUCCESS}✔${NC} bothub-nlp-nlu-worker" || echo "${DANGER}✖${NC} bothub-nlp-nlu-worker"
	@cd bothub-nlp-nlu-worker-on-demand \
		&& PIPENV_DONT_LOAD_ENV=1 pipenv run lint \
		&& echo "${SUCCESS}✔${NC} bothub-nlp-nlu-worker-on-demand" || echo "${DANGER}✖${NC} bothub-nlp-nlu-worker-on-demand"


# Utils

## Colors
SUCCESS = \033[0;32m
INFO = \033[0;36m
WARNING = \033[0;33m
DANGER = \033[0;31m
NC = \033[0m
