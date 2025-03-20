"""
Tests for character progression service and API endpoints.
"""
import pytest
from uuid import UUID, uuid4
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import os

# Create a new test client instead of importing from main
from fastapi import FastAPI
from app.api import character_progression

test_app = FastAPI()
test_app.include_router(character_progression.router)

# Import directly from services
from app.services.character_progression import (
    add_experience,
    calculate_xp_reward,
    _process_level_up,
    _create_level_up_message,
    _format_ability_name,
    _get_ability_type
)
from app.utils.character_defaults import get_level_xp_requirements, get_class_level_bonuses

client = TestClient(test_app)

# Mock user data for testing
test_user = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "test@example.com",
    "username": "testuser",
    "is_active": True,
    "role": "user"
}

# Mock character data for testing
test_character = {
    "id": "223e4567-e89b-12d3-a456-426614174000",
    "name": "Aragorn",
    "character_class": "warrior",
    "level": 1,
    "experience": 0,
    "stats": {
        "strength": 15,
        "dexterity": 12,
        "constitution": 14,
        "intelligence": 10,
        "wisdom": 12,
        "charisma": 13,
        "health": 100,
        "mana": 50
    },
    "abilities": {
        "passive": ["Rest", "Toughness"],
        "active": ["Attack", "Power Strike"],
        "special": []
    },
    "created_by": test_user["id"]
}

# Helper function to create test token
def get_test_token():
    from app.auth.jwt import create_access_token
    return create_access_token({"sub": test_user["id"]})

# === Unit Tests ===

def test_format_ability_name():
    """Test the ability name formatting function."""
    assert _format_ability_name("power_strike") == "Power Strike"
    assert _format_ability_name("arcane_missile") == "Arcane Missile"
    assert _format_ability_name("berserker rage") == "Berserker Rage"

def test_get_ability_type():
    """Test the ability type determination function."""
    assert _get_ability_type("power_strike", "warrior") == "active"
    assert _get_ability_type("improved_critical", "warrior") == "passive"
    assert _get_ability_type("berserker_rage", "warrior") == "special"
    assert _get_ability_type("arcane_recovery", "wizard") == "passive"
    assert _get_ability_type("unknown_ability", "any_class") == "active"  # Default

@pytest.mark.asyncio
async def test_calculate_xp_reward():
    """Test XP reward calculation for different actions."""
    # Test simple reward case without randomness
    with patch("random.uniform", return_value=0.9):  # Fix randomness to 90%
        # Test combat rewards
        combat_easy = await calculate_xp_reward("combat", "easy", True)
        combat_hard = await calculate_xp_reward("combat", "hard", True)
        combat_failed = await calculate_xp_reward("combat", "medium", False)
        
        # With controlled randomness, the values should be predictable
        assert combat_easy == 90  # 100 * 0.9
        assert combat_hard == 360  # 400 * 0.9
        assert combat_failed == 90  # 200 * 0.5 * 0.9 rounded to nearest 5
        
        # Test quest rewards
        quest_major = await calculate_xp_reward("quest", "major", True)
        assert quest_major == 1080  # 1200 * 0.9
        
        # Test unknown action type (should use defaults)
        unknown = await calculate_xp_reward("unknown_type", "medium", True)
        assert unknown == 90  # Default medium (100) * 0.9

def test_create_level_up_message():
    """Test level up notification message creation."""
    level_up_data = {
        "level": 2,
        "character_class": "warrior",
        "stat_changes": {
            "strength": {"old": 15, "new": 17, "change": "+2"},
            "constitution": {"old": 14, "new": 15, "change": "+1"}
        },
        "ability_changes": [
            {
                "name": "Improved Combat Techniques",
                "description": "A powerful warrior ability that allows you to use Improved Combat Techniques.",
                "type": "passive"
            }
        ]
    }
    
    message = _create_level_up_message("Aragorn", 2, level_up_data)
    
    assert "Aragorn has reached level 2" in message
    assert "Strength: 15 → 17" in message
    assert "Constitution: 14 → 15" in message
    assert "Improved Combat Techniques" in message

@pytest.mark.asyncio
async def test_process_level_up():
    """Test the level up processing function."""
    # Setup initial character data
    character = test_character.copy()
    stats = character["stats"].copy()
    abilities = character["abilities"].copy()
    
    # Process level up to level 2
    level_up_data = await _process_level_up(character, 2, "warrior", stats, abilities)
    
    # Verify level up data
    assert level_up_data["level"] == 2
    assert level_up_data["character_class"] == "warrior"
    
    # Check stat changes (warrior level 2 should get strength and constitution)
    new_stats = level_up_data["new_stats"]
    assert new_stats["strength"] > stats["strength"]
    
    # Check ability changes (warrior level 2 should get new abilities)
    new_abilities = level_up_data["new_abilities"]
    assert len(new_abilities["passive"]) >= len(abilities["passive"])

# === API Integration Tests ===

@pytest.fixture(autouse=True)
def mock_get_current_active_user():
    with patch("app.auth.jwt.get_current_active_user", return_value=test_user):
        with patch("app.api.character_progression.get_current_active_user", return_value=test_user):
            yield

@pytest.fixture
def mock_add_experience():
    with patch("app.api.character_progression.add_experience") as mock_func:
        # Configure the mock to return a success response
        async def _mock_add_experience(*args, **kwargs):
            return {
                "success": True,
                "xp_gained": 500,
                "xp_total": 500,
                "level": 1,
                "level_ups": None
            }
        mock_func.side_effect = _mock_add_experience
        yield mock_func

@pytest.fixture(autouse=True)
def mock_supabase():
    # Create a mock for the supabase client
    mock_result = MagicMock()
    mock_result.data = [test_character]
    
    mock_table = MagicMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = mock_result
    mock_table.insert.return_value = mock_table
    mock_table.update.return_value = mock_table
    
    mock_supabase = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    with patch("app.database.connection.supabase", mock_supabase):
        with patch("app.services.character_progression.supabase", mock_supabase):
            with patch("app.api.character_progression.supabase", mock_supabase):
                with patch("app.services.notification_service.supabase", mock_supabase):
                    yield mock_supabase

@pytest.fixture
def mock_calculate_xp_reward():
    with patch("app.api.character_progression.calculate_xp_reward") as mock_func:
        # Configure the mock to return a fixed XP value
        async def _mock_calculate_xp_reward(*args, **kwargs):
            return 250
        mock_func.side_effect = _mock_calculate_xp_reward
        yield mock_func

@pytest.fixture
def mock_get_level_xp():
    with patch("app.utils.character_defaults.get_level_xp_requirements") as mock_func:
        mock_func.return_value = {1: 0, 2: 1000, 3: 3000, 4: 6000, 5: 10000}
        yield mock_func

def test_add_character_experience_endpoint(mock_supabase, mock_add_experience):
    """Test the add experience API endpoint."""
    character_id = test_character["id"]
    xp_data = {"xp_amount": 500}
    
    # Make the API request
    response = client.post(
        f"/character-progression/{character_id}/experience",
        json=xp_data,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["xp_gained"] == 500
    assert response.json()["xp_total"] == 500

def test_add_action_reward_endpoint(mock_supabase):
    """Test the action reward API endpoint."""
    character_id = test_character["id"]
    reward_data = {
        "action_type": "combat",
        "difficulty": "hard",
        "success": True
    }
    
    # Update mock to return a successful update
    updated_character = test_character.copy()
    updated_character["experience"] = 400  # Approximately what a hard combat should give
    mock_supabase.table().update().eq().execute.return_value.data = [updated_character]
    
    # Make the API request
    response = client.post(
        f"/character-progression/{character_id}/reward",
        json=reward_data,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["action"]["type"] == "combat"
    assert response.json()["action"]["difficulty"] == "hard"
    assert response.json()["action"]["success"] is True
    assert "xp_awarded" in response.json()["action"]

def test_get_next_level_info_endpoint(mock_supabase, mock_get_level_xp):
    """Test the next level info API endpoint."""
    character_id = test_character["id"]
    
    # Make the API request
    response = client.get(
        f"/character-progression/{character_id}/next-level",
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert "current_level" in response.json()
    assert "next_level" in response.json()
    assert "current_xp" in response.json()
    assert "xp_required" in response.json() or "xp_for_next_level" in response.json()
    assert "progress_percentage" in response.json()

def test_get_level_requirements_endpoint(mock_supabase, mock_get_level_xp):
    """Test the level requirements API endpoint."""
    character_id = test_character["id"]
    
    # Make the API request
    response = client.get(
        f"/character-progression/{character_id}/levels",
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "level_requirements" in response.json() or "class_level_bonuses" in response.json()
    
    # Check for nested data if available
    if "level_requirements" in response.json():
        assert isinstance(response.json()["level_requirements"], dict)
    if "class_level_bonuses" in response.json():
        assert isinstance(response.json()["class_level_bonuses"], dict)

def test_unauthorized_access(mock_supabase):
    """Test unauthorized access to another user's character."""
    # Create a character that belongs to another user
    other_user_id = str(uuid4())
    other_character = test_character.copy()
    other_character["id"] = str(uuid4())
    other_character["created_by"] = other_user_id
    
    # Update the mock to return this character
    mock_supabase.table().select().eq().execute.return_value.data = [other_character]
    
    # Try to add experience to this character
    response = client.post(
        f"/character-progression/{other_character['id']}/experience",
        json={"xp_amount": 100},
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Should fail with 403 Forbidden
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_level_up_notification(mock_supabase, mock_get_level_xp):
    """Test level up notification functionality."""
    character_id = test_character["id"]
    
    # Configure mocks to simulate a level up
    async def _mock_level_up(*args, **kwargs):
        # Return XP above the level threshold
        xp_amount = 1050  # Just over level threshold
        return {
            "success": True,
            "xp_gained": xp_amount,
            "xp_total": xp_amount,
            "level": 2,
            "level_ups": [
                {
                    "level": 2,
                    "character_class": "warrior",
                    "stat_changes": {"strength": {"old": 10, "new": 12, "change": "+2"}},
                    "ability_changes": [{"name": "New Ability", "type": "active"}]
                }
            ]
        }
    
    with patch("app.api.character_progression.add_experience", side_effect=_mock_level_up):
        # Make the API request to add XP
        response = client.post(
            f"/character-progression/{character_id}/experience",
            json={"xp_amount": 1050},
            headers={"Authorization": f"Bearer {get_test_token()}"}
        )
        
        # Verify response
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["level_ups"] is not None
        assert len(response.json()["level_ups"]) == 1
        assert response.json()["level_ups"][0]["level"] == 2

def test_reward_character_xp_endpoint(mock_supabase, mock_add_experience, mock_calculate_xp_reward):
    """Test the reward XP API endpoint."""
    character_id = test_character["id"]
    reward_data = {
        "action_type": "quest",
        "difficulty": "medium",
        "success": True
    }
    
    # Make the API request
    response = client.post(
        f"/character-progression/{character_id}/reward",
        json=reward_data,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "xp_gained" in response.json()
    assert response.json()["xp_total"] == 500  # From our mock

def test_character_level_up(mock_supabase):
    """Test a character leveling up from XP gain."""
    character_id = test_character["id"]
    xp_amount = 1500  # Enough to level up to level 2
    
    # Initial character at level 1
    initial_character = test_character.copy()
    mock_supabase.table().select().eq().execute.return_value.data = [initial_character]
    
    # Set up mock for the character after leveling up
    leveled_up_character = test_character.copy()
    leveled_up_character["level"] = 2
    leveled_up_character["experience"] = 1500
    leveled_up_character["stats"]["strength"] += 1  # Level up bonus
    mock_supabase.table().update().eq().execute.return_value.data = [leveled_up_character]
    
    # Make the API request to add XP
    response = client.post(
        f"/character-progression/{character_id}/experience",
        json={"xp_amount": xp_amount},
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check the response
    assert response.status_code == 200
    response_data = response.json()
    
    # Assert level up information
    assert "previous_level" in response_data
    assert "new_level" in response_data
    assert response_data["new_level"] > response_data["previous_level"]
    assert "level_ups" in response_data
    assert len(response_data["level_ups"]) > 0
    assert "character" in response_data
    assert response_data["character"]["level"] >= response_data["previous_level"]

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
