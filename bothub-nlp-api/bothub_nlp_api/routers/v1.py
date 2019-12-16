from typing import Optional

from fastapi import Depends, Form, APIRouter, Header, HTTPException
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
async def parse_handler(
    text: str = Form(...),
    language: str = Form(default=None),
    rasa_format: Optional[str] = Form(default=False),
    repository_version: Optional[int] = Form(default=None),
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):

    return parse._parse(Authorization, text, language, rasa_format, repository_version)


@router.get(r"/parse/?", response_model=ParseResponse, deprecated=True)
async def parse_handler(
    text: str,
    language: str = None,
    rasa_format: Optional[str] = False,
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):

    return parse._parse(Authorization, text, language, rasa_format)


@router.options(r"/parse/?", status_code=204, include_in_schema=False)
async def parse_options():
    return {}


@router.post(r"/train/?", response_model=TrainResponse)
async def train_handler(
    request: Request = Depends(AuthorizationRequired()),
    repository_version: Optional[int] = Form(default=None),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    result = train.train_handler(Authorization, repository_version)
    if result.get("status") and result.get("error"):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.options(r"/train/?", status_code=204, include_in_schema=False)
async def train_options():
    return {}


# @router.get(r"/info/?", response_model=InfoResponse)
@router.get(r"/info/?")
async def info_handler(
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    repository_authorization = get_repository_authorization(Authorization)
    info = backend().request_backend_parse("info", repository_authorization)
    if info.get('detail'):
        raise HTTPException(status_code=400, detail=info)
    info["intents"] = info["intents_list"]
    info.pop("intents_list")
    return info


@router.options(r"/info/?", status_code=204, include_in_schema=False)
async def info_options():
    return {}


@router.post(r"/evaluate/?", response_model=EvaluateResponse)
async def evaluate_handler(
    language: str = Form(default=None),
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    result = evaluate.evaluate_handler(Authorization, language)
    if result.get("status") and result.get("error"):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.options(r"/evaluate/?", status_code=204, include_in_schema=False)
async def evaluate_options():
    return {}
