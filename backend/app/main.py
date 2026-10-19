import os
from typing import List
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# --- OpenTelemetry Imports ---
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from .database import Base, engine, get_db
from .models import StoryModel
from .schemas import StoryCreate, StoryResponse
from .services import generate_story_service

# --- Setup OpenTelemetry OTLP Exporters ---
OTEL_COLLECTOR_URL = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")

# Traces setup
trace.set_tracer_provider(TracerProvider())
tracer_provider = trace.get_tracer_provider()
span_exporter = OTLPSpanExporter(endpoint=OTEL_COLLECTOR_URL, insecure=True)
tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))

# Metrics setup
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=OTEL_COLLECTOR_URL, insecure=True)
)
meter_provider = MeterProvider(metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

# Auto-instrument Logging
LoggingInstrumentor().instrument(set_logging_format=True)

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)

# Auto-instrument SQLAlchemy engine
SQLAlchemyInstrumentor().instrument(engine=engine)

app = FastAPI(title="Sci-Fi Stories Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-instrument FastAPI
FastAPIInstrumentor.instrument_app(app)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/v1/stories", response_model=List[StoryResponse])
def list_stories(db: Session = Depends(get_db)):
    return db.query(StoryModel).order_by(StoryModel.id.desc()).all()


@app.post("/api/v1/stories", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
async def create_story(story_in: StoryCreate, db: Session = Depends(get_db)):
    ai_text, model_used = await generate_story_service(story_in)

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