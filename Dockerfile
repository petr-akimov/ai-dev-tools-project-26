FROM python:3.12-slim

WORKDIR /app

# Install uv package manager
RUN pip install uv

# Install all backend dependencies directly
RUN uv pip install --system \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.32.0" \
    "sqlalchemy>=2.0.35" \
    "pydantic>=2.9.0" \
    "gigachat>=0.1.0" \
    "python-dotenv>=1.0.1" \
    "opentelemetry-api>=1.20.0" \
    "opentelemetry-sdk>=1.20.0" \
    "opentelemetry-instrumentation-fastapi>=0.41b0" \
    "opentelemetry-instrumentation-sqlalchemy>=0.41b0" \
    "opentelemetry-instrumentation-logging>=0.41b0" \
    "opentelemetry-exporter-otlp>=1.20.0"

COPY backend/ /app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]