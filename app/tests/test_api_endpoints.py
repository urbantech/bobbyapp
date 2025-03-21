import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.jwt import create_access_token
import os
import json
from unittest.mock import patch, MagicMock

client = TestClient(app)

# Mock user data for testing
test_user = {
    "id": "test-user-id",
    "email": "test@example.com",
    "username": "testuser",
    "is_active": True,
    "role": "user"
}

# Helper function to create test token
def get_test_token():
    return create_access_token({"sub": test_user["id"]})

# Mock the auth dependency to bypass authentication for tests
@pytest.fixture(autouse=True)
def mock_get_current_active_user():
    with patch("app.auth.jwt.get_current_active_user", return_value=test_user):
        yield

# Mock Supabase for testing
@pytest.fixture(autouse=True)
def mock_supabase():
    # Create a mock for the supabase module
    mock_result = MagicMock()
    mock_result.data = []
    
    mock_table = MagicMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = mock_result
    mock_table.insert.return_value = mock_table
    mock_table.update.return_value = mock_table
    mock_table.delete.return_value = mock_table
    
    mock_storage = MagicMock()
    mock_storage.from_.return_value = mock_storage
    mock_storage.upload.return_value = "mock_file_path"
    mock_storage.get_public_url.return_value = "https://example.com/mock_file_path"
    
    mock_supabase = MagicMock()
    mock_supabase.table.return_value = mock_table
    mock_supabase.storage = mock_storage
    
    with patch("app.database.connection.supabase", mock_supabase):
        with patch("app.api.auth.supabase", mock_supabase):
            with patch("app.api.characters.supabase", mock_supabase):
                with patch("app.api.conversations.supabase", mock_supabase):
                    with patch("app.api.dice.supabase", mock_supabase):
                        with patch("app.api.quests.supabase", mock_supabase):
                            with patch("app.api.multimodal.supabase", mock_supabase):
                                with patch("app.services.conversation_service.supabase", mock_supabase):
                                    yield mock_supabase

# Test root endpoint
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "status" in response.json()

# Test health check endpoint
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# === Auth API Tests ===
def test_register_user():
    user_data = {
        "email": "new_user@example.com",
        "password": "secure_password",
        "username": "newuser"
    }
    
    response = client.post(f"{os.getenv('API_PREFIX', '/api/v1')}/auth/register", json=user_data)
    assert response.status_code == 201

def test_login_user():
    login_data = {
        "email": "test@example.com",
        "password": "password"
    }
    
    response = client.post(f"{os.getenv('API_PREFIX', '/api/v1')}/auth/token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

# === Character API Tests ===
def test_create_character(mock_supabase):
    # Setup mock to return character data
    mock_data = {
        "id": "test-character-id",
        "name": "Test Character",
        "character_class": "warrior",
        "created_by": test_user["id"]
    }
    mock_supabase.table().insert().execute.return_value.data = [mock_data]
    
    character_data = {
        "name": "Test Character",
        "character_class": "warrior",
        "backstory": "A mighty warrior from the north",
        "personality": {"traits": ["brave", "honorable"]}
    }
    
    response = client.post(
        f"{os.getenv('API_PREFIX', '/api/v1')}/characters", 
        json=character_data,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == "Test Character"

def test_get_user_characters(mock_supabase):
    # Setup mock to return characters
    mock_data = [
        {
            "id": "test-character-id-1",
            "name": "Character 1",
            "character_class": "warrior",
            "created_by": test_user["id"]
        },
        {
            "id": "test-character-id-2",
            "name": "Character 2",
            "character_class": "wizard",
            "created_by": test_user["id"]
        }
    ]
    mock_supabase.table().select().eq().execute.return_value.data = mock_data
    
    response = client.get(
        f"{os.getenv('API_PREFIX', '/api/v1')}/characters",
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Character 1"
    assert response.json()[1]["name"] == "Character 2"

# === Dice API Tests ===
def test_roll_dice(mock_supabase):
    # Setup mock to return dice roll
    mock_data = {
        "id": "test-dice-roll-id",
        "type": "d20",
        "count": 1,
        "result": 15,
        "user_id": test_user["id"]
    }
    mock_supabase.table().insert().execute.return_value.data = [mock_data]
    
    dice_data = {
        "type": "d20",
        "count": 1,
        "modifier": 0
    }
    
    response = client.post(
        f"{os.getenv('API_PREFIX', '/api/v1')}/dice",
        json=dice_data,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    assert response.status_code == 201
    assert response.json()["type"] == "d20"
    assert "result" in response.json()

# === Quest API Tests ===
def test_create_quest(mock_supabase):
    # Setup mock to return quest data
    mock_data = {
        "id": "test-quest-id",
        "title": "Test Quest",
        "description": "A test quest",
        "created_by": test_user["id"],
        "status": "active"
    }
    mock_supabase.table().insert().execute.return_value.data = [mock_data]
    
    quest_data = {
        "title": "Test Quest",
        "description": "A test quest",
        "objectives": ["Objective 1", "Objective 2"],
        "difficulty": "medium"
    }
    
    response = client.post(
        f"{os.getenv('API_PREFIX', '/api/v1')}/quests",
        json=quest_data,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    assert response.status_code == 201
    assert response.json()["title"] == "Test Quest"

# === Conversation API Tests ===
def test_create_conversation(mock_supabase):
    # Setup mock to return conversation data
    mock_data = {
        "id": "test-conversation-id",
        "user_id": test_user["id"],
        "character_id": "test-character-id",
        "title": "Test Conversation"
    }
    mock_supabase.table().insert().execute.return_value.data = [mock_data]
    
    # Setup character mock
    character_mock = {
        "id": "test-character-id",
        "name": "Test Character"
    }
    mock_supabase.table().select().eq().execute.return_value.data = [character_mock]
    
    conversation_data = {
        "character_id": "test-character-id",
        "title": "Test Conversation"
    }
    
    response = client.post(
        f"{os.getenv('API_PREFIX', '/api/v1')}/conversations",
        json=conversation_data,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    assert response.status_code == 201
    assert response.json()["title"] == "Test Conversation"

def test_add_message(mock_supabase):
    # Setup mocks for conversation, message, and character
    conversation_mock = {
        "id": "test-conversation-id",
        "user_id": test_user["id"],
        "character_id": "test-character-id"
    }
    
    message_mock = {
        "id": "test-message-id",
        "conversation_id": "test-conversation-id",
        "content": "Hello character",
        "is_user_message": True
    }
    
    character_response_mock = {
        "id": "test-message-response-id",
        "conversation_id": "test-conversation-id",
        "content": "Hello user",
        "is_user_message": False
    }
    
    # Configure mocks
    mock_supabase.table().select().eq().execute.return_value.data = [conversation_mock]
    mock_supabase.table().insert().execute.side_effect = [
        MagicMock(data=[message_mock]),
        MagicMock(data=[character_response_mock])
    ]
    
    message_data = {
        "content": "Hello character",
        "sender_type": "user"
    }
    
    response = client.post(
        f"{os.getenv('API_PREFIX', '/api/v1')}/conversations/test-conversation-id/messages",
        json=message_data,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    assert response.status_code == 200
    # In our updated implementation, we return the character's response
    assert response.json()["is_user_message"] == False

# === Multimodal API Tests ===
def test_upload_file(mock_supabase):
    # Setup mocks
    conversation_mock = {
        "id": "test-conversation-id",
        "user_id": test_user["id"]
    }
    
    multimodal_mock = {
        "id": "test-multimodal-id",
        "conversation_id": "test-conversation-id",
        "type": "image",
        "content_url": "https://example.com/test.jpg"
    }
    
    # Configure mock
    mock_supabase.table().select().eq().execute.return_value.data = [conversation_mock]
    mock_supabase.table().insert().execute.return_value.data = [multimodal_mock]
    
    # Create a simple test file
    test_file_content = b"test image content"
    
    response = client.post(
        f"{os.getenv('API_PREFIX', '/api/v1')}/multimodal/upload?conversation_id=test-conversation-id",
        files={"file": ("test.jpg", test_file_content, "image/jpeg")},
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert "file_url" in response.json()

# Run tests if this file is executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
