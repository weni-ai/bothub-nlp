import logging

from sentry_sdk import init
from fastapi import FastAPI

from bothub_nlp_api import settings
from bothub_nlp_api.routers import v1
from bothub_nlp_api.routers import v2


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

# Sentry
if settings.BOTHUB_NLP_SENTRY_CLIENT:
    init(
        dsn=settings.BOTHUB_NLP_SENTRY,
        environment=settings.ENVIRONMENT,
    )

app = FastAPI(title="Bothub NLP", version="3.0", description="", docs_url="/")

app.include_router(v1.router, tags=["v1"])

app.include_router(v2.router, prefix="/v2", tags=["v2"])
