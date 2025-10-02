from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field
from datetime import datetime, timezone

SourceType = Literal["open311","here_incident","here_flow","tweet","news","manual"]
EventType = Literal["water_main_break","road_closure","lane_restriction","congestion"]
IncidentStatus = Literal["active","resolved"]
ActionStatus = Literal["pending","done"]

class Evidence(BaseModel):
    evidence_id: str
    source_type: SourceType
    type: EventType
    lat: float
    lng: float
    radius_m: Optional[int] = 80
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    confidence: float = 0.6
    url: Optional[str] = None
    raw: Dict = Field(default_factory=dict)
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WhyCard(BaseModel):
    rules_fired: List[str] = []
    cross_checks: List[str] = []

class ActionStep(BaseModel):
    step: str
    owner: str = "Ops"
    priority: int = 2
    status: ActionStatus = "pending"

class Incident(BaseModel):
    id: str
    type: EventType
    status: IncidentStatus = "active"
    lat: float
    lng: float
    severity: float
    confidence: float
    summary: Optional[str] = None
    impact: Optional[Dict] = None
    sources: List[Dict] = []
    why: WhyCard = WhyCard()
    actions: List[ActionStep] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))