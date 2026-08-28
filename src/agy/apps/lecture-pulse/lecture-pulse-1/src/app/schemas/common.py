from typing import Optional, Generic, List, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar('T')


class ErrorBody(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    message: str
    details: Optional[object] = None


class ErrorEnvelope(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    error: ErrorBody


class ListResponse(BaseModel, Generic[T]):
    """Design-mandated list envelope: {"items": [...]}."""
    items: List[T]
