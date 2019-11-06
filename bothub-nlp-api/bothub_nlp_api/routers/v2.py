from fastapi import Depends, APIRouter, Header, HTTPException
from starlette.requests import Request

from bothub_nlp_api.handlers import evaluate
from bothub_nlp_api.handlers import parse
from bothub_nlp_api.handlers import train
from bothub_nlp_api.models import ParseRequest
from bothub_nlp_api.models import EvaluateRequest
from bothub_nlp_api.models import ParseResponse
from bothub_nlp_api.models import TrainResponse
from bothub_nlp_api.models import InfoResponse
from bothub_nlp_api.models import EvaluateResponse
from bothub_nlp_api.utils import backend, AuthorizationRequired
from bothub_nlp_api.utils import get_repository_authorization

router = APIRouter(redirect_slashes=False)


@router.post(r"/parse/?", response_model=ParseResponse)
async def parsepost_handler(
    item: ParseRequest,
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):

    return parse._parse(Authorization, item.text, item.language, item.rasa_format)


@router.options(r"/parse/?", status_code=204, include_in_schema=False)
async def parse_options():
    return {}


@router.post(r"/train/?", response_model=TrainResponse)
async def train_handler(
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    result = train.train_handler(Authorization)
    if result.get("status") and result.get("error"):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.options(r"/train/?", status_code=204, include_in_schema=False)
async def train_options():
    return {}


@router.get(r"/info/?", response_model=InfoResponse)
async def info_handler(
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
async def evaluate_handler(
    item: EvaluateRequest,
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    result = evaluate.evaluate_handler(Authorization, item.language)
    if result.get("status") and result.get("error"):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.options(r"/evaluate/?", status_code=204, include_in_schema=False)
async def evaluate_options():
    return {}
