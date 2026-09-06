import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from app.main import app
from app.db import Base, get_db
from app.models import Memory


SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


Base.metadata.create_all(bind=test_engine)

def clear_test_database():
    db = TestingSessionLocal()
    try:
        db.query(Memory).delete()
        db.commit()
    finally:
        db.close()

@pytest.fixture(autouse=True)
def clean_database():
    clear_test_database()

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Kivi Golden Goose backend is running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_memory():
    response = client.post(
        "/api/observe",
        json={
            "observed": "Kavin",
            "intended": "Kavin"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] in [
        "New memory created",
        "Existing memory updated"
    ]


def test_get_memories():
    response = client.get("/api/memories")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_transform_text():
    client.post(
        "/api/observe",
        json={
            "observed": "adithya",
            "intended": "aaditya"
        }
    )

    client.post(
        "/api/observe",
        json={
            "observed": "adithya",
            "intended": "aaditya"
        }
    )

    client.post(
        "/api/observe",
        json={
            "observed": "adithya",
            "intended": "aaditya"
        }
    )

    response = client.post(
        "/api/transform",
        json={
            "text": "adithya is here"
        }
    )


    assert response.status_code == 200
    assert response.json()["original"] == "adithya is here"
    assert response.json()["transformed"] == "aaditya is here"

def test_transform_with_punctuation():
    client.post(
        "/api/observe",
        json={
            "observed": "adithya",
            "intended": "aaditya"
        }
    )

    client.post(
        "/api/observe",
        json={
            "observed": "adithya",
            "intended": "aaditya"
        }
    )

    client.post(
        "/api/observe",
        json={
            "observed": "adithya",
            "intended": "aaditya"
        }
    )

    response = client.post(
        "/api/transform",
        json={
            "text": "Adithya, is here!"
        }
    )

    assert response.status_code == 200
    assert response.json()["transformed"] == "aaditya, is here!"

def test_invalid_confidence():
    response = client.patch(
        "/api/memories/1",
        json={
            "confidence": 1.5
        }
    )

    assert response.status_code == 422

def test_update_nonexistent_memory():
    response = client.patch(
        "/api/memories/999",
        json={
            "confidence": 0.8
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Memory not found"

def test_invalid_status():
    response = client.patch(
        "/api/memories/1",
        json={
            "status": "hello"
        }
    )

    assert response.status_code == 422

def test_invalid_memory_update():
    response = client.patch(
        "/api/memories/1",
        json={
            "confidence": 2.0,
            "status": "unknown"
        }
    )

    assert response.status_code == 422

def test_delete_nonexistent_memory():
    response = client.delete("/api/memories/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Memory not found"

def test_delete_memory():
    create_response = client.post(
        "/api/observe",
        json={
            "observed": "DeleteTest",
            "intended": "DeleteTest"
        }
    )

    assert create_response.status_code == 200

    memories = client.get("/api/memories").json()

    memory_id = None

    for memory in memories:
        if memory["canonical"] == "deletetest":
            memory_id = memory["id"]
            break

    assert memory_id is not None

    response = client.delete(
        f"/api/memories/{memory_id}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Memory deleted successfully"

    response = client.get("/api/memories")

    memories = response.json()

    assert all(
        memory["id"] != memory_id
        for memory in memories
    )

def test_valid_disabled_status():
    create_response = client.post(
        "/api/observe",
        json={
            "observed": "DisableTest",
            "intended": "DisableTest"
        }
    )

    assert create_response.status_code == 200

    memories = client.get("/api/memories").json()

    memory_id = None

    for memory in memories:
        if memory["canonical"] == "disabletest":
            memory_id = memory["id"]
            break

    assert memory_id is not None

    response = client.patch(
        f"/api/memories/{memory_id}",
        json={
            "status": "disabled"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "disabled"

def test_memory_confirmation():
    # First observation
    response = client.post(
        "/api/observe",
        json={
            "observed": "Rahul",
            "intended": "Rahul"
        }
    )

    assert response.status_code == 200

    # Second observation
    response = client.post(
        "/api/observe",
        json={
            "observed": "Rahul",
            "intended": "Rahul"
        }
    )

    assert response.status_code == 200

    # Third observation
    response = client.post(
        "/api/observe",
        json={
            "observed": "Rahul",
            "intended": "Rahul"
        }
    )

    assert response.status_code == 200

    memories = client.get("/api/memories").json()

    memory = None

    for item in memories:
        if item["canonical"] == "rahul":
            memory = item
            break

    assert memory is not None
    assert memory["evidence_count"] == 3
    assert memory["status"] == "confirmed"

def test_reset_memories():
    # Create a memory
    response = client.post(
        "/api/observe",
        json={
            "observed": "ResetTest",
            "intended": "ResetTest"
        }
    )

    assert response.status_code == 200

    # Confirm memory exists
    memories = client.get("/api/memories").json()
    assert len(memories) > 0

    # Reset all memories
    response = client.delete("/api/reset")

    assert response.status_code == 200
    assert response.json()["message"] == "All memories have been reset"

    # Verify database is empty
    response = client.get("/api/memories")

    assert response.status_code == 200
    assert response.json() == []