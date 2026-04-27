import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


@pytest.fixture
def mock_redis():
    """Mock Redis for testing"""
    with patch("main.r") as mock:
        yield mock


def test_health_endpoint(mock_redis):
    """Test health check endpoint returns ok"""
    mock_redis.ping.return_value = True
    
    from main import app
    client = TestClient(app)
    
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_job(mock_redis):
    """Test creating a new job"""
    mock_redis.rpush.return_value = 1
    mock_redis.hset.return_value = True
    
    from main import app
    client = TestClient(app)
    
    response = client.post("/jobs", json={"task": "test-task"})
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert isinstance(data["job_id"], str)
    assert len(data["job_id"]) > 0


def test_get_job_status(mock_redis):
    """Test retrieving job status"""
    mock_redis.hgetall.return_value = {
        "status": "pending",
        "task": "test-task"
    }
    
    from main import app
    client = TestClient(app)
    
    response = client.get("/jobs/test-job-123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert data["task"] == "test-task"
    assert data["job_id"] == "test-job-123"


def test_job_not_found(mock_redis):
    """Test requesting non-existent job returns 404"""
    mock_redis.hgetall.return_value = {}
    
    from main import app
    client = TestClient(app)
    
    response = client.get("/jobs/nonexistent-job")
    assert response.status_code == 404
