"""
Test schemas for data validation.
"""
import pytest
from datetime import datetime
from app.schemas.user import UserCreate, UserResponse, Token
from app.schemas.character import CharacterCreate, CharacterResponse
from app.schemas.conversation import ConversationCreate, MessageCreate
from app.schemas.dice import DiceRollCreate, DiceRollResponse
from app.schemas.quest import QuestCreate, QuestResponse, QuestStatus

def test_user_schema():
    """Test user schemas validation."""
    # Test UserCreate
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword"
    }
    user = UserCreate(**user_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "securepassword"
    
    # Test UserResponse
    user_response_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "testuser",
        "email": "test@example.com",
        "subscription_level": "free",
        "created_at": datetime.now()
    }
    user_response = UserResponse(**user_response_data)
    assert user_response.id == "123e4567-e89b-12d3-a456-426614174000"
    assert user_response.username == "testuser"
    
    # Test Token
    token_data = {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    }
    token = Token(**token_data)
    assert token.token_type == "bearer"  # default value

def test_character_schema():
    """Test character schemas validation."""
    # Test CharacterCreate
    char_data = {
        "name": "Gandalf",
        "character_class": "wizard",
        "backstory": "A wise wizard from the west",
        "personality": {
            "traits": ["wise", "kind", "stern"],
            "quirks": ["loves fireworks"]
        }
    }
    character = CharacterCreate(**char_data)
    assert character.name == "Gandalf"
    assert character.character_class == "wizard"
    assert "wise" in character.personality["traits"]

def test_quest_schema():
    """Test quest schemas validation."""
    # Test QuestCreate
    quest_data = {
        "name": "Find the Ring",
        "description": "Journey to Mount Doom and destroy the One Ring",
        "difficulty": "hard",
        "reward": {
            "xp": 1000,
            "gold": 500,
            "items": ["Elven Cloak"]
        }
    }
    quest = QuestCreate(**quest_data)
    assert quest.name == "Find the Ring"
    assert quest.difficulty == "hard"
    assert quest.reward["xp"] == 1000
    
    # Test QuestResponse
    quest_response_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Find the Ring",
        "description": "Journey to Mount Doom and destroy the One Ring",
        "difficulty": "hard",
        "reward": {
            "xp": 1000,
            "gold": 500,
            "items": ["Elven Cloak"]
        },
        "status": "Pending",
        "assigned_to": "123e4567-e89b-12d3-a456-426614174001",
        "created_at": datetime.now()
    }
    quest_response = QuestResponse(**quest_response_data)
    assert quest_response.id == "123e4567-e89b-12d3-a456-426614174000"
    assert quest_response.status == "Pending"

def test_dice_roll_schema():
    """Test dice roll schemas validation."""
    # Test DiceRollCreate
    dice_data = {
        "dice_type": 20,
        "character_id": "123e4567-e89b-12d3-a456-426614174000"
    }
    dice_roll = DiceRollCreate(**dice_data)
    assert dice_roll.dice_type == 20
    assert dice_roll.character_id == "123e4567-e89b-12d3-a456-426614174000"

if __name__ == "__main__":
    # Run tests manually
    test_user_schema()
    test_character_schema()
    test_quest_schema()
    test_dice_roll_schema()
    print("All schema tests passed!")
