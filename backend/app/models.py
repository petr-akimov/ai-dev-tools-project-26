from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base


class StoryModel(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    heroes = Column(Text, nullable=False)          # Who (e.g., "Mr. White - scientist, Lady Spice - rogue")
    when_happens = Column(String, nullable=False)  # When (e.g., "Year 2659")
    where_happens = Column(String, nullable=False) # Where (e.g., "Planet Pluck, abandoned dock")
    summary = Column(Text, nullable=False)        # Short plot/summary
    ai_story = Column(Text, nullable=True)        # Generated story by GigaChat
    model_used = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())