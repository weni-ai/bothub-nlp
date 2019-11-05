from fastapi import Depends, APIRouter, Header
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

    result = await parse._parse(request, item.text, item.language, item.rasa_format)
    return result


@router.options(r"/parse/?", status_code=204, include_in_schema=False)
async def parse_options():
    return {}


@router.post(r"/train/?", response_model=TrainResponse)
def train_handler(
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    return train.train_handler(request)


@router.options(r"/train/?", status_code=204, include_in_schema=False)
async def train_options():
    return {}


@router.get(r"/info/?", response_model=InfoResponse)
def info_handler(
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    repository_authorization = get_repository_authorization(request)
    info = backend().request_backend_parse("info", repository_authorization)
    info["intents"] = info["intents_list"]
    info.pop("intents_list")
    return info


@router.options(r"/info/?", status_code=204, include_in_schema=False)
async def info_options():
    return {}


@router.post(r"/evaluate/?", response_model=EvaluateResponse)
def evaluate_handler(
    item: EvaluateRequest,
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    return evaluate.evaluate_handler(request, item.language)


@router.options(r"/evaluate/?", status_code=204, include_in_schema=False)
async def evaluate_options():
    return {}
