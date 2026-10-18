FROM python:3.12-slim

WORKDIR /app

# Install uv package manager
RUN pip install uv

COPY backend/ /app/
RUN uv pip install --system -r pyproject.toml || uv pip install --system fastapi uvicorn sqlalchemy gigachat pydantic python-dotenv

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]