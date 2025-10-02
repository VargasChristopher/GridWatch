from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class PublicSource(BaseModel):
    type: str
    confidence: float

class PublicAction(BaseModel):
    step: str
    owner: str
    status: str  # "pending" | "done" | etc.

class IncidentOut(BaseModel):
    id: str
    type: str                 # e.g. "power_outage","water_line_break","gas_leak","internet_outage","accident"
    status: str               # "active" | "resolved" | "monitoring"
    lat: float
    lng: float
    severity: float
    confidence: float
    summary: Optional[str] = None
    sources: List[PublicSource]
    actions: List[PublicAction]
    created_at: datetime
    time: Optional[datetime] = None
