from typing import List
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import StoryModel
from .schemas import StoryCreate, StoryResponse
from .services import generate_story_service

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sci-Fi Stories Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    # Health check endpoint for container probes and monitoring
    return {"status": "ok"}


@app.get("/api/v1/stories", response_model=List[StoryResponse])
def list_stories(db: Session = Depends(get_db)):
    # Retrieve all generated sci-fi chronicles from SQLite database
    return db.query(StoryModel).order_by(StoryModel.id.desc()).all()


@app.post("/api/v1/stories", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
async def create_story(story_in: StoryCreate, db: Session = Depends(get_db)):
    # Generate sci-fi story text using GigaChat-2 service
    ai_text, model_used = await generate_story_service(story_in)

    # Save record to database
    db_story = StoryModel(
        title=story_in.title,
        heroes=story_in.heroes,
        when_happens=story_in.when_happens,
        where_happens=story_in.where_happens,
        summary=story_in.summary,
        ai_story=ai_text,
        model_used=model_used,
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story