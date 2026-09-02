from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ComplaintCreate(BaseModel):
    customer_name: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
    customer_email: str = Field(..., pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    customer_phone: str = Field(..., min_length=1)
    account_number: str = Field(..., min_length=1)
    account_type: str = Field(..., min_length=1)
    product_type: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    priority: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    channel: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    narrative: str = Field(..., min_length=1)
    disputed_amount: float = Field(..., ge=0.0)
    sla_target_hours: int = Field(168, ge=1)  # Default 7 days (168 hours)

class StatusTransitionRequest(BaseModel):
    status: str = Field(..., pattern="^(NEW|IN_INVESTIGATION|UNDER_REVIEW|APPROVED|RESOLVED|ESCALATED)$")
    actor_role: str = Field(..., min_length=1)
    actor_name: str = Field(..., min_length=1)
    details: Optional[str] = None

class AssignHandlerRequest(BaseModel):
    assigned_to: str = Field(..., min_length=1)
    actor_role: str = Field(..., min_length=1)
    actor_name: str = Field(..., min_length=1)
    details: Optional[str] = None

class InvestigationRequest(BaseModel):
    root_cause: str = Field(..., min_length=1)
    investigation_notes: str = Field(..., min_length=1)
    actor_role: str = Field(..., min_length=1)
    actor_name: str = Field(..., min_length=1)

class RedressRequest(BaseModel):
    refund_amount: float = Field(..., ge=0.0)
    goodwill_amount: float = Field(..., ge=0.0)
    interest_amount: float = Field(..., ge=0.0)
    actor_role: str = Field(..., min_length=1)
    actor_name: str = Field(..., min_length=1)

class SupervisorReviewRequest(BaseModel):
    review_decision: str = Field(..., pattern="^(APPROVED|REJECTED)$")
    supervisor_name: str = Field(..., min_length=1)
    supervisor_notes: Optional[str] = None
    actor_role: str = "Supervisor"
    actor_name: Optional[str] = None

class AuditLogResponse(BaseModel):
    id: int
    complaint_id: int
    timestamp: datetime
    actor_role: str
    actor_name: str
    action_type: str
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    details: Optional[str] = None
    metadata_json: Optional[str] = None

    class Config:
        from_attributes = True

class ComplaintResponse(BaseModel):
    id: int
    reference_number: str
    customer_name: str
    customer_id: str
    customer_email: str
    customer_phone: str
    account_number: str
    account_type: str
    product_type: str
    category: str
    priority: str
    channel: str
    subject: str
    narrative: str
    disputed_amount: float
    status: str
    assigned_to: Optional[str] = None
    root_cause: Optional[str] = None
    investigation_notes: Optional[str] = None
    refund_amount: float
    goodwill_amount: float
    interest_amount: float
    total_redress: float
    supervisor_notes: Optional[str] = None
    review_decision: str
    supervisor_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    sla_target_hours: int
    resolved_at: Optional[datetime] = None
    audit_logs: List[AuditLogResponse] = []

    class Config:
        from_attributes = True

class WorkbenchStatsResponse(BaseModel):
    total: int
    under_review: int
    in_investigation: int
    resolved: int
    escalated: int
    total_redress_paid: float
