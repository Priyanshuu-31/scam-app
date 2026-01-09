from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

class EntityType(str, Enum):
    UPI = "upi"
    PHONE = "phone"
    URL = "url"
    MESSAGE_TEXT = "message_text"
    OTHER = "other"

class RiskLevel(str, Enum):
    SAFE = "Safe"
    CAUTION = "Caution"
    CRITICAL = "Critical"

class ReportIn(BaseModel):
    value: str
    type: EntityType
    description: Optional[str] = None
    evidence_urls: List[str] = []
    tags: List[str] = []

class RiskScore(BaseModel):
    value: str
    risk_score: int
    level: RiskLevel
    report_count: int
    last_reported_at: Optional[datetime] = None
