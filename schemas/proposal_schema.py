from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Recommendation(BaseModel):
    model_id: str
    grade_id: str
    engine_id: str
    vehicle_price: int  # Price from VehicleModels
    reasons: List[str]
    est_lead_weeks: Optional[int] = None


class NormalizedRequirements(BaseModel):
    budget_max: Optional[int]
    passenger_count: Optional[int]
    priority: Optional[str]
    fuel_pref: Optional[str]


class ProposalAgentResponse(BaseModel):
    recommendations: List[Recommendation]
    normalized_requirements: NormalizedRequirements
    next_action_hint: Optional[str]
    metadata: dict = Field(default_factory=dict)


class ProposalQuery(BaseModel):
    user_query: str
    budget_max: Optional[int]
    passenger_count: Optional[int]
    priority: Optional[str]
    fuel_pref: Optional[str]
