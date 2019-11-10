from typing import List, Dict, Any

from pydantic import BaseModel


class ParseRequest(BaseModel):
    text: str
    language: str = None
    rasa_format: bool = False


class EvaluateRequest(BaseModel):
    language: str = None


class IntentResponse(BaseModel):
    name: Any
    confidence: Any


class IntentRankingResponse(BaseModel):
    name: Any
    confidence: Any


class ParseResponse(BaseModel):
    intent: IntentResponse
    intent_ranking: List[IntentRankingResponse]
    labels_list: List[str]
    entities_list: List[str]
    entities: Dict[str, List[Dict[str, Any]]]
    text: str
    update_id: int
    language: str


class TrainResponse(BaseModel):
    SUPPORTED_LANGUAGES: List[str]
    languages_report: Dict[str, Dict[str, str]]


class CategoriesList(BaseModel):
    icon: str
    id: int
    name: str


class EvaluateLanguages(BaseModel):
    language: int


class OtherLabel(BaseModel):
    entities: List[str]
    examples__count: int
    repository: str
    value: str


class InfoResponse(BaseModel):
    absolute_url: str
    algorithm: str
    authorization: Any
    available_languages: List[str]
    available_request_authorization: bool
    categories: List[CategoriesList]
    categories_list: List[str]
    created_at: str
    description: str
    entities: Any
    entities_list: Any
    evaluate_languages_count: Dict[str, int]
    examples__count: int
    intents: List[str]
    is_private: bool
    labels: List[str]
    labels_list: List[str]
    language: str
    languages_ready_for_train: Dict[str, bool]
    languages_warnings: Dict[str, str]
    name: str
    nlp_server: str
    other_label: OtherLabel
    owner: int
    owner__nickname: str
    ready_for_train: bool
    request_authorization: bool
    requirements_to_train: Dict[str, str]
    slug: str
    use_competing_intents: bool
    use_language_model_featurizer: bool
    use_name_entities: bool
    uuid: str


class EvaluateResponse(BaseModel):
    language: str
    status: str
    update_id: int
    evaluate_id: int
    evaluate_version: int
