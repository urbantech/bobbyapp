import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    """Test that the root endpoint returns 200 OK"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to BobbyApp API", "status": "online"}

def test_health_check():
    """Test that the health endpoint returns healthy status"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# Add more tests as needed for API endpoints
# For tests requiring authentication, you'll need to mock the authentication process
