"""
Tests for inventory service and API endpoints.
"""
import pytest
from uuid import UUID, uuid4
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import os

# Create a new test client instead of importing from main
from fastapi import FastAPI
from app.api import inventory

test_app = FastAPI()
test_app.include_router(inventory.router, prefix="/api/v1/inventory")

from app.schemas.inventory import (
    ItemCreate,
    ItemResponse,
    InventoryItemCreate,
    InventoryItemResponse,
    ItemType,
    ItemRarity,
    EquipmentSlot
)

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
    "created_by": test_user["id"]
}

# Mock item data for testing
test_item = {
    "id": "323e4567-e89b-12d3-a456-426614174000",
    "name": "Steel Longsword",
    "description": "A well-crafted steel longsword",
    "item_type": "weapon",
    "properties": {
        "damage": "1d8+1",
        "weight": 3,
        "value": 15
    },
    "rarity": "common",
    "equipment_slot": "main_hand",
    "requirements": {
        "level": 1,
        "strength": 10
    },
    "created_by": test_user["id"]
}

# Mock inventory item data for testing
test_inventory_item = {
    "id": "423e4567-e89b-12d3-a456-426614174000",
    "character_id": test_character["id"],
    "item_id": test_item["id"],
    "quantity": 1,
    "equipped": False,
    "created_by": test_user["id"]
}

# Helper function to create test token
def get_test_token():
    from app.auth.jwt import create_access_token
    return create_access_token({"sub": test_user["id"]})

# === Fixtures ===

@pytest.fixture(autouse=True)
def mock_get_current_active_user():
    with patch("app.auth.jwt.get_current_active_user", return_value=test_user):
        yield

@pytest.fixture(autouse=True)
def mock_supabase():
    # Create a mock for the supabase client
    mock_char_result = MagicMock()
    mock_char_result.data = [test_character]
    
    mock_item_result = MagicMock()
    mock_item_result.data = [test_item]
    
    mock_inv_result = MagicMock()
    mock_inv_result.data = [test_inventory_item]
    
    # Create mock for character table
    char_table = MagicMock()
    char_table.select.return_value = char_table
    char_table.eq.return_value = char_table
    char_table.execute.return_value = mock_char_result
    
    # Create mock for item table
    item_table = MagicMock()
    item_table.select.return_value = item_table
    item_table.eq.return_value = item_table
    item_table.execute.return_value = mock_item_result
    
    # Insert operations
    item_table.insert.return_value = MagicMock()
    item_table.insert().execute.return_value.data = [test_item]
    
    # Create mock for inventory table
    inv_table = MagicMock()
    inv_table.select.return_value = inv_table
    inv_table.eq.return_value = inv_table
    inv_table.execute.return_value = mock_inv_result
    
    # Update operations
    inv_table.update.return_value = MagicMock()
    inv_table.update().eq.return_value = MagicMock()
    inv_table.update().eq().execute.return_value.data = [test_inventory_item]
    
    # Configure the mock to return different tables
    mock_supabase = MagicMock()
    
    def table_side_effect(name):
        if name == "characters":
            return char_table
        elif name == "items":
            return item_table
        elif name == "inventory":
            return inv_table
        return MagicMock()
    
    mock_supabase.table.side_effect = table_side_effect
    
    with patch("app.database.connection.supabase", mock_supabase):
        with patch("app.api.inventory.supabase", mock_supabase):
            with patch("app.services.inventory_service.supabase", mock_supabase):
                with patch("app.services.notification_service.supabase", mock_supabase):
                    yield mock_supabase

# === Unit Tests for Schemas ===

def test_item_create_schema():
    """Test the ItemCreate schema."""
    item_data = {
        "name": "Steel Longsword",
        "description": "A well-crafted steel longsword",
        "item_type": "weapon",
        "rarity": "common",
        "value": 15,
        "weight": 3.0,
        "equipment_slot": "main_hand",
        "requirements": {
            "level": 1,
            "strength": 10
        }
    }
    
    item = ItemCreate(**item_data)
    assert item.name == "Steel Longsword"
    assert item.item_type == ItemType.WEAPON
    assert item.rarity == ItemRarity.COMMON
    assert item.equipment_slot == EquipmentSlot.MAIN_HAND
    assert item.value == 15
    assert item.weight == 3.0
    assert item.requirements["level"] == 1

def test_inventory_item_create_schema():
    """Test the InventoryItemCreate schema."""
    inventory_item_data = {
        "character_id": "223e4567-e89b-12d3-a456-426614174000",
        "item_id": "323e4567-e89b-12d3-a456-426614174000",
        "quantity": 1,
        "equipped": False
    }
    
    inventory_item = InventoryItemCreate(**inventory_item_data)
    assert str(inventory_item.character_id) == "223e4567-e89b-12d3-a456-426614174000"
    assert str(inventory_item.item_id) == "323e4567-e89b-12d3-a456-426614174000"
    assert inventory_item.quantity == 1
    assert inventory_item.equipped is False

# === API Integration Tests ===

def test_create_item(mock_supabase):
    """Test the create item API endpoint."""
    item_data = {
        "name": "Magic Staff",
        "description": "A staff imbued with arcane energy",
        "item_type": "weapon",
        "value": 50,
        "weight": 2.0,
        "rarity": "uncommon",
        "equipment_slot": "two_hand",
        "requirements": {
            "level": 3,
            "intelligence": 12
        }
    }

    # Configure mock to return the created item
    created_item = item_data.copy()
    created_item["id"] = "new-item-id"
    created_item["created_by"] = test_user["id"]
    
    # Update the insert operation on the items table
    item_table = mock_supabase.table("items")
    item_table.insert.return_value = MagicMock()
    item_table.insert().execute.return_value.data = [created_item]
    
    # Make the API request
    response = client.post(
        "/api/v1/inventory/items",
        json=item_data,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check the response
    assert response.status_code == 201
    assert response.json()["name"] == "Magic Staff"
    assert response.json()["id"] == "new-item-id"

def test_get_items(mock_supabase):
    """Test the get items API endpoint."""
    # Configure mock to return multiple items
    items = [
        test_item,
        {
            "id": "different-item-id",
            "name": "Magic Staff",
            "description": "A staff imbued with arcane energy",
            "item_type": "weapon",
            "properties": {"damage": "1d6+2"},
            "rarity": "uncommon",
            "created_by": test_user["id"]
        }
    ]
    mock_supabase.table().select().execute.return_value.data = items
    
    # Make the API request
    response = client.get(
        "/api/v1/inventory/items",
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Steel Longsword"
    assert response.json()[1]["name"] == "Magic Staff"

def test_add_item_to_character(mock_supabase):
    """Test adding an item to a character's inventory."""
    character_id = test_character["id"]
    item_id = test_item["id"]
    
    inventory_data = {
        "item_id": item_id,
        "quantity": 1
    }
    
    # Configure mock to return the created inventory item
    created_inv_item = {
        "id": "new-inventory-item-id",
        "character_id": character_id,
        "item_id": item_id,
        "quantity": 1,
        "equipped": False,
        "created_by": test_user["id"]
    }
    mock_supabase.table().insert().execute.return_value.data = [created_inv_item]
    
    # Make the API request
    response = client.post(
        f"/api/v1/inventory/characters/{character_id}/items",
        json=inventory_data,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check the response
    assert response.status_code == 201
    assert response.json()["character_id"] == character_id
    assert response.json()["item_id"] == item_id
    assert response.json()["quantity"] == 1
    assert response.json()["equipped"] is False

def test_get_character_inventory(mock_supabase):
    """Test getting a character's inventory."""
    character_id = test_character["id"]
    
    # Configure mock to return inventory with item details
    inventory_with_items = [
        {
            "id": test_inventory_item["id"],
            "character_id": character_id,
            "item_id": test_item["id"],
            "quantity": 1,
            "equipped": False,
            "item": test_item
        }
    ]
    mock_supabase.table().select().eq().execute.return_value.data = inventory_with_items
    
    # Make the API request
    response = client.get(
        f"/api/v1/inventory/characters/{character_id}/items",
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == test_inventory_item["id"]
    assert response.json()[0]["character_id"] == character_id
    assert "item" in response.json()[0]
    assert response.json()[0]["item"]["name"] == "Steel Longsword"

def test_equip_item(mock_supabase):
    """Test equipping an item."""
    character_id = test_character["id"]
    inventory_id = test_inventory_item["id"]
    
    equip_data = {
        "equipped": True,
        "slot": "main_hand"
    }
    
    # Configure mock to return the updated inventory item
    updated_inv_item = test_inventory_item.copy()
    updated_inv_item["equipped"] = True
    updated_inv_item["slot"] = "main_hand"
    mock_supabase.table().update().eq().execute.return_value.data = [updated_inv_item]
    
    # Make the API request
    response = client.patch(
        f"/api/v1/inventory/characters/{character_id}/items/{inventory_id}/equip",
        json=equip_data,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["equipped"] is True
    assert response.json()["slot"] == "main_hand"

def test_unequip_item(mock_supabase):
    """Test unequipping an item."""
    character_id = test_character["id"]
    inventory_id = test_inventory_item["id"]
    
    # First set up the item as equipped
    equipped_inv_item = test_inventory_item.copy()
    equipped_inv_item["equipped"] = True
    equipped_inv_item["slot"] = "main_hand"
    mock_supabase.table().select().eq().execute.return_value.data = [equipped_inv_item]
    
    # Configure mock to return the updated inventory item after unequipping
    unequipped_inv_item = test_inventory_item.copy()
    unequipped_inv_item["equipped"] = False
    unequipped_inv_item["slot"] = None
    mock_supabase.table().update().eq().execute.return_value.data = [unequipped_inv_item]
    
    # Make the API request
    response = client.patch(
        f"/api/v1/inventory/characters/{character_id}/items/{inventory_id}/unequip",
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["equipped"] is False
    assert response.json()["slot"] is None

def test_remove_item_from_character(mock_supabase):
    """Test removing an item from a character's inventory."""
    character_id = test_character["id"]
    inventory_id = test_inventory_item["id"]
    
    # Configure mock for successful deletion
    mock_supabase.table().delete().eq().execute.return_value.data = [test_inventory_item]
    
    # Make the API request
    response = client.delete(
        f"/api/v1/inventory/characters/{character_id}/items/{inventory_id}",
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert response.json()["message"] == "Item removed from inventory"

def test_transfer_item_between_characters(mock_supabase):
    """Test transferring an item between characters."""
    character_id = test_character["id"]
    inventory_id = test_inventory_item["id"]
    target_character_id = "different-character-id"
    
    transfer_data = {
        "target_character_id": target_character_id,
        "quantity": 1
    }
    
    # Configure mock to return the owner character
    mock_supabase.table().select().eq("id", character_id).execute.return_value.data = [test_character]
    
    # Configure mock to return the target character 
    target_character = test_character.copy()
    target_character["id"] = target_character_id
    target_character["name"] = "Legolas"
    mock_supabase.table().select().eq("id", target_character_id).execute.return_value.data = [target_character]
    
    # Configure mock for successful transfer
    transferred_inv_item = test_inventory_item.copy()
    transferred_inv_item["character_id"] = target_character_id
    mock_supabase.table().insert().execute.return_value.data = [transferred_inv_item]
    
    # Make the API request
    response = client.post(
        f"/api/v1/inventory/characters/{character_id}/items/{inventory_id}/transfer",
        json=transfer_data,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check the response
    assert response.status_code == 200
    assert "success" in response.json()
    assert response.json()["success"] is True

def test_unauthorized_inventory_access(mock_supabase):
    """Test unauthorized access to another user's character inventory."""
    # Create a character owned by a different user
    other_character = test_character.copy()
    other_character["id"] = "other-character-id"
    other_character["created_by"] = "different-user-id"
    mock_supabase.table().select().eq().execute.return_value.data = [other_character]
    
    # Try to access this character's inventory
    response = client.get(
        f"/api/v1/inventory/characters/{other_character['id']}/items",
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    
    # Check that the request is forbidden
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
