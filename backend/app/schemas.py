from typing import Optional
from pydantic import BaseModel, ConfigDict


class StoryCreate(BaseModel):
    title: str
    heroes: str
    when_happens: str
    where_happens: str
    summary: str


class StoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    heroes: str
    when_happens: str
    where_happens: str
    summary: str
    ai_story: Optional[str] = None
    model_used: Optional[str] = None