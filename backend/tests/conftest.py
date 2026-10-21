from typing import Generator
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Создаем тестовую SQLite базу в памяти (in-memory) для изоляции тестов
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database() -> Generator[None, None, None]:
    """Создает чистую базу данных для каждого теста и удаляет после."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session) -> Generator[TestClient, None, None]:
    """Фикстура тестового клиента FastAPI с подмененной тестовой БД."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_gigachat():
    """Автоматически мокирует внешний сервис GigaChat во всех тестах."""
    with patch("app.services.generate_story_service") as mock_service:
        # Возвращаем предсказуемый мок-результат генерации
        mock_service.return_value = (
            "Mocked sci-fi short story text about deep space adventures.",
            "mock-gigachat-model"
        )
        yield mock_service