import bothub_backend
from fastapi import HTTPException, Header
from starlette.requests import Request

import bothub_nlp_api.settings


def backend():
    return bothub_backend.get_backend(
        "bothub_backend.bothub.BothubBackend", bothub_nlp_api.settings.BOTHUB_ENGINE_URL
    )


NEXT_LANGS = {
    "english": ["en"],
    "portuguese": ["pt", "pt_br"],
    "pt": ["pt_br"],
    "pt-br": ["pt_br"],
    "br": ["pt_br"],
}


class AuthorizationIsRequired(HTTPException):
    def __init__(self):
        self.status_code = 401
        self.detail = "Authorization is required"


class ValidationError(HTTPException):
    def __init__(self, message):
        self.status_code = 400
        self.detail = message


def get_repository_authorization(authorization_header_value):
    authorization_uuid = authorization_header_value and authorization_header_value[7:]

    if not authorization_uuid:
        return False

    return authorization_uuid


class AuthorizationRequired:
    async def __call__(
        self,
        request: Request,
        Authorization: str = Header(..., description="Bearer your_key"),
    ):
        if request.method == "OPTIONS":
            return True

        repository_authorization = get_repository_authorization(Authorization)
        if not repository_authorization:
            raise HTTPException(status_code=401, detail="Authorization is required")
        return True
