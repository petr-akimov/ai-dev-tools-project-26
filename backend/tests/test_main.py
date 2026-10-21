from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Проверка доступности эндпоинта /health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_stories_empty(client: TestClient) -> None:
    """Проверка получения пустого списка историй при старте."""
    response = client.get("/api/v1/stories")
    assert response.status_code == 200
    assert response.json() == []


def test_create_story_success(client: TestClient) -> None:
    """Проверка успешного создания и сохранения новой sci-fi истории."""
    payload = {
        "title": "Quantum Horizon",
        "heroes": "Dr. Vance - physicist, Jax - cyborg scout",
        "when_happens": "Year 3000",
        "where_happens": "Orbit of Kepler-186f",
        "summary": "Crew discovers an alien artifact drifting near the space station."
    }

    response = client.post("/api/v1/stories", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["id"] is not None
    assert data["title"] == payload["title"]
    assert data["heroes"] == payload["heroes"]
    assert data["when_happens"] == payload["when_happens"]
    assert data["where_happens"] == payload["where_happens"]
    assert data["summary"] == payload["summary"]
    assert "Mocked sci-fi short story" in data["ai_story"]
    assert data["model_used"] == "mock-gigachat-model"

    # Проверяем, что история появилась в общем списке /api/v1/stories
    list_response = client.get("/api/v1/stories")
    assert list_response.status_code == 200
    stories = list_response.json()
    assert len(stories) == 1
    assert stories[0]["title"] == "Quantum Horizon"