"""
API routes for inventory management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import Dict, Any, List, Optional
from uuid import UUID

from app.schemas.inventory import (
    ItemCreate,
    ItemResponse,
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryUpdate,
    InventoryTransfer,
    InventoryEquipRequest
)
from app.auth.jwt import get_current_active_user
from app.database.connection import supabase
from app.services.inventory_service import (
    create_item,
    add_item_to_inventory,
    remove_item_from_inventory,
    equip_item,
    unequip_item,
    get_character_inventory,
    get_equipped_items,
    transfer_item
)

router = APIRouter(prefix="/inventory", tags=["inventory"])


# Item management routes (admin only)
@router.post("/items", response_model=Dict[str, Any])
async def create_new_item(item: ItemCreate, current_user = Depends(get_current_active_user)):
    """Create a new item (admin only)"""
    result = await create_item(
        name=item.name,
        description=item.description,
        item_type=item.item_type,
        rarity=item.rarity,
        value=item.value,
        weight=item.weight,
        stackable=item.stackable,
        max_stack=item.max_stack or 1,
        effects=item.effects,
        requirements=item.requirements,
        equipment_slot=item.equipment_slot,
        stats=item.stats,
        metadata=item.metadata,
        image_url=item.image_url
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to create item")
        )
    
    return result


@router.get("/items", response_model=List[ItemResponse])
async def get_items(
    current_user = Depends(get_current_active_user),
    item_type: Optional[str] = None,
    rarity: Optional[str] = None,
    equipment_slot: Optional[str] = None,
    name_search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get items with optional filtering"""
    # Build query
    query = supabase.table("items").select("*")
    
    # Apply filters
    if item_type:
        query = query.eq("item_type", item_type)
    
    if rarity:
        query = query.eq("rarity", rarity)
    
    if equipment_slot:
        query = query.eq("equipment_slot", equipment_slot)
    
    if name_search:
        query = query.ilike("name", f"%{name_search}%")
    
    # Apply pagination
    result = query.range(skip, skip + limit - 1).execute()
    
    return result.data


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: UUID, current_user = Depends(get_current_active_user)):
    """Get a specific item by ID"""
    result = supabase.table("items").select("*").eq("id", str(item_id)).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    return result.data[0]


# Character inventory routes
@router.get("/character/{character_id}", response_model=Dict[str, Any])
async def get_inventory(
    character_id: UUID,
    current_user = Depends(get_current_active_user),
    include_item_details: bool = Query(True)
):
    """Get a character's inventory"""
    user_id = current_user.get("id")
    
    # Check character ownership
    character_result = supabase.table("characters").select("created_by").eq("id", str(character_id)).execute()
    
    if not character_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
    
    character = character_result.data[0]
    
    # Verify ownership
    if character.get("created_by") != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this character's inventory"
        )
    
    # Get inventory
    result = await get_character_inventory(character_id, include_item_details)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to get character inventory")
        )
    
    return result


@router.get("/character/{character_id}/equipped", response_model=Dict[str, Any])
async def get_character_equipped_items(character_id: UUID, current_user = Depends(get_current_active_user)):
    """Get a character's equipped items"""
    user_id = current_user.get("id")
    
    # Check character ownership
    character_result = supabase.table("characters").select("created_by").eq("id", str(character_id)).execute()
    
    if not character_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
    
    character = character_result.data[0]
    
    # Verify ownership
    if character.get("created_by") != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this character's equipped items"
        )
    
    # Get equipped items
    result = await get_equipped_items(character_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to get equipped items")
        )
    
    return result


@router.post("/character/{character_id}/add", response_model=Dict[str, Any])
async def add_to_inventory(
    character_id: UUID,
    item_data: Dict[str, Any],
    current_user = Depends(get_current_active_user)
):
    """
    Add an item to a character's inventory
    
    Example request body:
    ```json
    {
        "item_id": "uuid-here",
        "quantity": 1,
        "equipped": false,
        "custom_name": "Custom Item Name",
        "custom_description": "Custom description"
    }
    ```
    """
    user_id = current_user.get("id")
    
    # Check character ownership
    character_result = supabase.table("characters").select("created_by").eq("id", str(character_id)).execute()
    
    if not character_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
    
    character = character_result.data[0]
    
    # Verify ownership (only owner or admin can add items)
    if character.get("created_by") != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this character's inventory"
        )
    
    # Extract parameters
    item_id = item_data.get("item_id")
    if not item_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="item_id is required"
        )
    
    # Add item to inventory
    result = await add_item_to_inventory(
        character_id=character_id,
        item_id=UUID(item_id),
        quantity=item_data.get("quantity", 1),
        equipped=item_data.get("equipped", False),
        durability=item_data.get("durability"),
        custom_name=item_data.get("custom_name"),
        custom_description=item_data.get("custom_description"),
        custom_effects=item_data.get("custom_effects"),
        metadata=item_data.get("metadata")
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to add item to inventory")
        )
    
    return result


@router.post("/character/{character_id}/remove", response_model=Dict[str, Any])
async def remove_from_inventory(
    character_id: UUID,
    item_data: Dict[str, Any],
    current_user = Depends(get_current_active_user)
):
    """
    Remove an item from a character's inventory
    
    Example request body:
    ```json
    {
        "inventory_item_id": "uuid-here",
        "quantity": 1
    }
    ```
    """
    user_id = current_user.get("id")
    
    # Check character ownership
    character_result = supabase.table("characters").select("created_by").eq("id", str(character_id)).execute()
    
    if not character_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
    
    character = character_result.data[0]
    
    # Verify ownership (only owner or admin can remove items)
    if character.get("created_by") != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this character's inventory"
        )
    
    # Extract parameters
    inventory_item_id = item_data.get("inventory_item_id")
    if not inventory_item_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="inventory_item_id is required"
        )
    
    # Remove item from inventory
    result = await remove_item_from_inventory(
        character_id=character_id,
        inventory_item_id=UUID(inventory_item_id),
        quantity=item_data.get("quantity", 1)
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to remove item from inventory")
        )
    
    return result


@router.post("/character/{character_id}/equip", response_model=Dict[str, Any])
async def equip_inventory_item(
    character_id: UUID,
    equip_request: InventoryEquipRequest,
    current_user = Depends(get_current_active_user)
):
    """Equip or unequip an item"""
    user_id = current_user.get("id")
    
    # Check character ownership
    character_result = supabase.table("characters").select("created_by").eq("id", str(character_id)).execute()
    
    if not character_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
    
    character = character_result.data[0]
    
    # Verify ownership (only owner or admin can equip items)
    if character.get("created_by") != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this character's equipment"
        )
    
    # Equip or unequip item
    if equip_request.equip:
        result = await equip_item(character_id, equip_request.inventory_item_id)
    else:
        result = await unequip_item(character_id, equip_request.inventory_item_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to equip/unequip item")
        )
    
    return result


@router.post("/transfer", response_model=Dict[str, Any])
async def transfer_inventory_item(
    transfer_request: InventoryTransfer,
    current_user = Depends(get_current_active_user)
):
    """
    Transfer an item between characters
    
    Example request body:
    ```json
    {
        "from_character_id": "uuid-here",
        "to_character_id": "uuid-here",
        "items": [
            {
                "inventory_item_id": "uuid-here",
                "quantity": 1
            }
        ]
    }
    ```
    """
    user_id = current_user.get("id")
    
    # Check character ownership
    character_result = supabase.table("characters").select("id, created_by").in_("id", [str(transfer_request.from_character_id), str(transfer_request.to_character_id)]).execute()
    
    if len(character_result.data) != 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both characters not found"
        )
    
    # Verify ownership of both characters
    from_character = next((c for c in character_result.data if c.get("id") == str(transfer_request.from_character_id)), None)
    to_character = next((c for c in character_result.data if c.get("id") == str(transfer_request.to_character_id)), None)
    
    if (from_character.get("created_by") != user_id and current_user.get("role") != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to transfer items from this character"
        )
    
    # Process each item transfer
    results = []
    for item in transfer_request.items:
        inventory_item_id = item.get("inventory_item_id")
        quantity = item.get("quantity", 1)
        
        result = await transfer_item(
            transfer_request.from_character_id,
            transfer_request.to_character_id,
            UUID(inventory_item_id),
            quantity
        )
        
        results.append(result)
    
    # Check if any transfers failed
    failures = [r for r in results if not r.get("success")]
    if failures:
        return {
            "success": False,
            "message": "Some transfers failed",
            "results": results
        }
    
    return {
        "success": True,
        "message": "All transfers completed successfully",
        "results": results
    }
