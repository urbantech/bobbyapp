import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.jwt import create_access_token
import os
from unittest.mock import patch, MagicMock
import json
from unittest.mock import AsyncMock
from datetime import datetime

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
    # Mock data
    test_user = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": "$2b$12$QUoJVvCsEYo6SgPVqXjTQuHQqZvscbMc7iqM9i8J7b7dTYscUgsIi",  # Hash for "password"
        "created_at": "2023-01-01T00:00:00",
        "subscription_level": "free",
    }
    
    # Create a mock for the supabase client
    mock_supabase = MagicMock()
    
    # Set up mock for user table
    user_table = MagicMock()
    
    # For user registration
    mock_insert_result = MagicMock()
    new_user = {
        "id": "660e8400-e29b-41d4-a716-446655440000",
        "username": "newuser",
        "email": "new_user@example.com",
        "created_at": "2023-01-02T00:00:00",
        "subscription_level": "free"
    }
    mock_insert_result.data = [new_user]
    
    user_table.insert.return_value = MagicMock()
    user_table.insert().execute.return_value = mock_insert_result
    
    # For email check during registration
    mock_empty_result = MagicMock()
    mock_empty_result.data = []
    
    # For login authentication
    mock_login_result = MagicMock()
    mock_login_result.data = [test_user]
    
    # Configure select with dynamic response based on query parameters
    def select_execute_side_effect(*args, **kwargs):
        # The actual implementation would check the chain of calls
        # For simplicity, we'll just return the appropriate mocked response
        return mock_login_result
    
    select_mock = MagicMock()
    select_mock.execute.side_effect = select_execute_side_effect
    
    # Setup for various select chains
    user_table.select.return_value = MagicMock()
    user_table.select().eq.return_value = select_mock
    
    # Special case for registration email check
    registration_check = MagicMock()
    registration_check.execute.return_value = mock_empty_result
    
    def eq_side_effect(field, value):
        if field == "email" and value == "new_user@example.com":
            # For registration, return empty result to allow registration
            return registration_check
        # For login, return mock with test user
        return select_mock
    
    user_table.select().eq.side_effect = eq_side_effect
    
    # Mock storage
    mock_storage = MagicMock()
    mock_storage.from_.return_value = mock_storage
    mock_storage.upload.return_value = "mock_file_path"
    mock_storage.get_public_url.return_value = "https://example.com/mock_file_path"
    
    mock_supabase.storage = mock_storage
    
    # Configure the mock to return different tables
    def table_side_effect(name):
        if name == "users":
            return user_table
        return MagicMock()
    
    mock_supabase.table.side_effect = table_side_effect
    
    # Apply the mock to all modules that use supabase
    with patch("app.database.connection.supabase", mock_supabase):
        with patch("app.auth.jwt.supabase", mock_supabase):
            with patch("app.api.auth.supabase", mock_supabase):
                with patch("app.api.characters.supabase", mock_supabase):
                    with patch("app.api.conversations.supabase", mock_supabase):
                        with patch("app.api.dice.supabase", mock_supabase):
                            with patch("app.api.quests.supabase", mock_supabase):
                                with patch("app.api.multimodal.supabase", mock_supabase):
                                    with patch("app.services.conversation_service.supabase", mock_supabase):
                                        with patch("app.services.inventory_service.supabase", mock_supabase):
                                            with patch("app.services.notification_service.supabase", mock_supabase):
                                                with patch("app.auth.jwt.verify_password", return_value=True):
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
    # Generate a unique email for this test run
    unique_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    test_email = f"test{unique_id}@example.com"
    
    # First register a user
    register_data = {
        "email": test_email,
        "password": "password",
        "username": f"testuser{unique_id}"
    }
    
    # Register the user
    register_response = client.post(f"{os.getenv('API_PREFIX', '/api/v1')}/auth/register", json=register_data)
    assert register_response.status_code == 201
    
    # Login with the registered user
    login_data = {
        "username": test_email,  # OAuth2 expects username field for email
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
