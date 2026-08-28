from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict


class TokenRequest(BaseModel):
    subject: str
    role: Literal['instructor', 'student']
    display_name: Optional[str] = None
    email: Optional[str] = None


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
    token_type: str = 'bearer'
    expires_in: int
    subject: str
    role: str


class MeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    subject: str
    role: str
    display_name: Optional[str] = None
