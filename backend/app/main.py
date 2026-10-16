from typing import List

from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import MatchModel
from .schemas import MatchCreate, MatchResponse
from .services import generate_recap_service

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sports League Scoreboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/v1/matches", response_model=List[MatchResponse])
def list_matches(db: Session = Depends(get_db)):
    return db.query(MatchModel).order_by(MatchModel.id.desc()).all()

@app.post("/api/v1/matches", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(match: MatchCreate, db: Session = Depends(get_db)):
    recap_text, model_used = await generate_recap_service(match)
    
    db_match = MatchModel(
        home_team=match.home_team,
        away_team=match.away_team,
        home_score=match.home_score,
        away_score=match.away_score,
        match_date=match.match_date,
        recap=recap_text,
        model_used=model_used
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match
    