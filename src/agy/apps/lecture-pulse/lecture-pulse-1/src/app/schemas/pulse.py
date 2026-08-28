from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class PulseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: int
    status: str
    created_at: datetime


class PulseResponseCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)


class PulseResponseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    pulse_id: int
    created_at: datetime


class PulseSentimentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    pulse_id: int
    total: int
    average: Optional[float] = None
    distribution: Dict[str, int]
