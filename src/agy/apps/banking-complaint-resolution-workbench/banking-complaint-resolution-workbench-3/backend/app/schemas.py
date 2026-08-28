from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class ActivityLogBase(BaseModel):
    action: str
    performed_by: str
    comments: Optional[str] = None

class ActivityLogResponse(ActivityLogBase):
    id: int
    complaint_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class ComplaintBase(BaseModel):
    customer_name: str
    account_number: str
    account_type: str
    severity: str
    description: str

class ComplaintCreate(ComplaintBase):
    pass

class ComplaintResponse(BaseModel):
    id: int
    customer_name: str
    account_number: str
    account_type: str
    severity: str
    status: str
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ComplaintDetailResponse(ComplaintResponse):
    activity_logs: List[ActivityLogResponse] = []

class TransitionRequest(BaseModel):
    new_status: str
    performed_by: Optional[str] = None
    comments: Optional[str] = None
