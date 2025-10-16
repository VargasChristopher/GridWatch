# gridwatch_config/schemas.py
from typing import List, Literal
from pydantic import BaseModel, Field

class Incident(BaseModel):
    type: Literal["traffic", "outage", "crime", "environment", "emergency"]
    lat: float
    lng: float
    severity: float
    confidence: float
    where: str
    etaMinutes: int
    sources: List[str]
    updatedAt: int

class IncidentsPayload(BaseModel):
    incidents: List[Incident] = Field(default_factory=list)
