from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GoalScorer(BaseModel):
    player: str
    minute: int = Field(..., ge=1, le=120)
    team: str

class MatchCreate(BaseModel):
    home_team: str
    away_team: str
    home_score: int = Field(..., ge=0)
    away_score: int = Field(..., ge=0)
    match_date: str
    scorers: List[GoalScorer] = []
    summary_notes: Optional[str] = None

class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    match_date: str
    recap: Optional[str] = None
    model_used: Optional[str] = None