from typing import Optional

from fastapi import Depends, Form, APIRouter, Header
from starlette.requests import Request

from bothub_nlp_api.handlers import evaluate
from bothub_nlp_api.handlers import parse
from bothub_nlp_api.handlers import train
from bothub_nlp_api.models import EvaluateResponse
from bothub_nlp_api.models import InfoResponse
from bothub_nlp_api.models import ParseResponse
from bothub_nlp_api.models import TrainResponse
from bothub_nlp_api.utils import AuthorizationRequired
from bothub_nlp_api.utils import backend
from bothub_nlp_api.utils import get_repository_authorization

router = APIRouter(redirect_slashes=False)


@router.post(r"/parse/?", response_model=ParseResponse)
def parse_handler(
    text: str = Form(...),
    language: str = Form(default=None),
    rasa_format: Optional[str] = Form(default=False),
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):

    return parse._parse(Authorization, text, language, rasa_format)


@router.options(r"/parse/?", status_code=204, include_in_schema=False)
async def parse_options():
    return {}


@router.post(r"/train/?", response_model=TrainResponse)
def train_handler(
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    return train.train_handler(Authorization)


@router.options(r"/train/?", status_code=204, include_in_schema=False)
async def train_options():
    return {}


@router.get(r"/info/?", response_model=InfoResponse)
def info_handler(
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    repository_authorization = get_repository_authorization(Authorization)
    info = backend().request_backend_parse("info", repository_authorization)
    info["intents"] = info["intents_list"]
    info.pop("intents_list")
    return info


@router.options(r"/info/?", status_code=204, include_in_schema=False)
async def info_options():
    return {}


@router.post(r"/evaluate/?", response_model=EvaluateResponse)
def evaluate_handler(
    language: str = Form(default=None),
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    return evaluate.evaluate_handler(Authorization, language)


@router.options(r"/evaluate/?", status_code=204, include_in_schema=False)
async def evaluate_options():
    return {}
