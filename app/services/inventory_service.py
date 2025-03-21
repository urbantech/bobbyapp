"""
Inventory service for managing character items and equipment.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from uuid import UUID

from app.database.connection import supabase
from app.schemas.inventory import ItemType, ItemRarity, EquipmentSlot
from app.services.notification_service import create_character_notification
from app.schemas.notification import NotificationPriority, NotificationType

logger = logging.getLogger(__name__)


async def get_item(item_id: UUID) -> Dict[str, Any]:
    """
    Retrieve item details by id.
    
    Args:
        item_id: UUID of the item
        
    Returns:
        Item data or None if not found
    """
    try:
        result = supabase.table("items").select("*").eq("id", str(item_id)).execute()
        
        if not result.data:
            logger.warning(f"Item {item_id} not found")
            return None
            
        return result.data[0]
    
    except Exception as e:
        logger.error(f"Error retrieving item {item_id}: {str(e)}")
        return None


async def create_item(
    name: str,
    description: str,
    item_type: str,
    rarity: str = "common",
    value: int = 0,
    weight: float = 0.0,
    stackable: bool = False,
    max_stack: int = 1,
    effects: Optional[List[Dict[str, Any]]] = None,
    requirements: Optional[Dict[str, Any]] = None,
    equipment_slot: Optional[str] = None,
    stats: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    image_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new item.
    
    Args:
        Various item properties
        
    Returns:
        Created item data or error
    """
    try:
        # Build item data
        item_data = {
            "name": name,
            "description": description,
            "item_type": item_type,
            "rarity": rarity,
            "value": value,
            "weight": weight,
            "stackable": stackable,
            "max_stack": max_stack
        }
        
        # Add optional fields if provided
        if effects:
            item_data["effects"] = effects
        
        if requirements:
            item_data["requirements"] = requirements
            
        if equipment_slot:
            item_data["equipment_slot"] = equipment_slot
            
        if stats:
            item_data["stats"] = stats
            
        if metadata:
            item_data["metadata"] = metadata
            
        if image_url:
            item_data["image_url"] = image_url
            
        # Insert into database
        result = supabase.table("items").insert(item_data).execute()
        
        if not result.data:
            logger.error(f"Failed to create item {name}")
            return {"success": False, "error": "Failed to create item"}
            
        return {"success": True, "item": result.data[0]}
        
    except Exception as e:
        logger.error(f"Error creating item {name}: {str(e)}")
        return {"success": False, "error": str(e)}


async def add_item_to_inventory(
    character_id: UUID,
    item_id: UUID,
    quantity: int = 1,
    equipped: bool = False,
    durability: Optional[int] = None,
    custom_name: Optional[str] = None,
    custom_description: Optional[str] = None,
    custom_effects: Optional[List[Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Add an item to a character's inventory.
    
    Args:
        character_id: UUID of character
        item_id: UUID of item to add
        quantity: Number of items to add
        equipped: Whether the item is equipped
        durability: Item durability
        custom_name: Custom item name
        custom_description: Custom item description
        custom_effects: Custom item effects
        metadata: Additional metadata
        
    Returns:
        Result of operation
    """
    try:
        # Check if character exists
        character_result = supabase.table("characters").select("id, name, created_by").eq("id", str(character_id)).execute()
        
        if not character_result.data:
            logger.error(f"Character {character_id} not found")
            return {"success": False, "error": "Character not found"}
            
        character = character_result.data[0]
        
        # Check if item exists
        item_result = supabase.table("items").select("*").eq("id", str(item_id)).execute()
        
        if not item_result.data:
            logger.error(f"Item {item_id} not found")
            return {"success": False, "error": "Item not found"}
            
        item = item_result.data[0]
        
        # If item is stackable, check if it already exists in inventory
        if item.get("stackable", False):
            existing_item = supabase.table("inventory").select("*").eq("character_id", str(character_id)).eq("item_id", str(item_id)).execute()
            
            if existing_item.data:
                # Update quantity
                current_quantity = existing_item.data[0].get("quantity", 0)
                new_quantity = current_quantity + quantity
                
                # Check if exceeds max stack
                max_stack = item.get("max_stack", 1)
                if max_stack > 0 and new_quantity > max_stack:
                    new_quantity = max_stack
                    
                # Update inventory item
                update_result = supabase.table("inventory").update({
                    "quantity": new_quantity,
                    "updated_at": "now()"
                }).eq("id", existing_item.data[0].get("id")).execute()
                
                if not update_result.data:
                    logger.error(f"Failed to update inventory for character {character_id}")
                    return {"success": False, "error": "Failed to update inventory"}
                    
                # Send notification
                user_id = character.get("created_by")
                if user_id:
                    await create_character_notification(
                        user_id=UUID(user_id),
                        character_id=character_id,
                        title=f"Item Added: {item.get('name')}",
                        message=f"Added {quantity} {item.get('name')} to {character.get('name')}'s inventory.",
                        priority=NotificationPriority.LOW
                    )
                
                return {
                    "success": True,
                    "inventory_item": update_result.data[0],
                    "message": f"Added {quantity} {item.get('name')} to inventory"
                }
        
        # Create new inventory entry
        inventory_data = {
            "character_id": str(character_id),
            "item_id": str(item_id),
            "quantity": quantity,
            "equipped": equipped
        }
        
        # Add optional fields if provided
        if durability is not None:
            inventory_data["durability"] = durability
            
        if custom_name:
            inventory_data["custom_name"] = custom_name
            
        if custom_description:
            inventory_data["custom_description"] = custom_description
            
        if custom_effects:
            inventory_data["custom_effects"] = custom_effects
            
        if metadata:
            inventory_data["metadata"] = metadata
            
        # Insert into database
        result = supabase.table("inventory").insert(inventory_data).execute()
        
        if not result.data:
            logger.error(f"Failed to add item to inventory for character {character_id}")
            return {"success": False, "error": "Failed to add item to inventory"}
        
        # Send notification
        user_id = character.get("created_by")
        if user_id:
            await create_character_notification(
                user_id=UUID(user_id),
                character_id=character_id,
                title=f"Item Acquired: {item.get('name')}",
                message=f"{character.get('name')} acquired {quantity} {item.get('name')}.",
                priority=NotificationPriority.LOW
            )
        
        return {
            "success": True,
            "inventory_item": result.data[0],
            "message": f"Added {quantity} {item.get('name')} to inventory"
        }
        
    except Exception as e:
        logger.error(f"Error adding item to inventory: {str(e)}")
        return {"success": False, "error": str(e)}


async def remove_item_from_inventory(
    character_id: UUID,
    inventory_item_id: UUID,
    quantity: int = 1
) -> Dict[str, Any]:
    """
    Remove an item from a character's inventory.
    
    Args:
        character_id: UUID of character
        inventory_item_id: UUID of inventory item
        quantity: Number of items to remove
        
    Returns:
        Result of operation
    """
    try:
        # Check if character exists
        character_result = supabase.table("characters").select("id, name").eq("id", str(character_id)).execute()
        
        if not character_result.data:
            logger.error(f"Character {character_id} not found")
            return {"success": False, "error": "Character not found"}
            
        # Check if inventory item exists and belongs to character
        inventory_result = supabase.table("inventory").select("*, items(*)").eq("id", str(inventory_item_id)).eq("character_id", str(character_id)).execute()
        
        if not inventory_result.data:
            logger.error(f"Inventory item {inventory_item_id} not found or does not belong to character {character_id}")
            return {"success": False, "error": "Inventory item not found"}
            
        inventory_item = inventory_result.data[0]
        current_quantity = inventory_item.get("quantity", 0)
        
        # Check if item is equipped
        if inventory_item.get("equipped", False):
            logger.warning(f"Cannot remove equipped item {inventory_item_id} from inventory")
            return {"success": False, "error": "Cannot remove equipped item from inventory"}
        
        # Calculate new quantity
        new_quantity = current_quantity - quantity
        
        if new_quantity < 0:
            logger.warning(f"Not enough items to remove {quantity} from inventory")
            return {"success": False, "error": f"Not enough items to remove (have {current_quantity}, trying to remove {quantity})"}
            
        if new_quantity == 0:
            # Remove item from inventory
            delete_result = supabase.table("inventory").delete().eq("id", str(inventory_item_id)).execute()
            
            if not delete_result.data:
                logger.error(f"Failed to remove item {inventory_item_id} from inventory")
                return {"success": False, "error": "Failed to remove item from inventory"}
                
            return {
                "success": True,
                "message": f"Removed item {inventory_item.get('items', {}).get('name', 'Unknown')} from inventory"
            }
        else:
            # Update quantity
            update_result = supabase.table("inventory").update({
                "quantity": new_quantity,
                "updated_at": "now()"
            }).eq("id", str(inventory_item_id)).execute()
            
            if not update_result.data:
                logger.error(f"Failed to update quantity for item {inventory_item_id}")
                return {"success": False, "error": "Failed to update item quantity"}
                
            return {
                "success": True,
                "inventory_item": update_result.data[0],
                "message": f"Removed {quantity} {inventory_item.get('items', {}).get('name', 'Unknown')} from inventory"
            }
    
    except Exception as e:
        logger.error(f"Error removing item from inventory: {str(e)}")
        return {"success": False, "error": str(e)}


async def equip_item(character_id: UUID, inventory_item_id: UUID) -> Dict[str, Any]:
    """
    Equip an item from a character's inventory.
    
    Args:
        character_id: UUID of character
        inventory_item_id: UUID of inventory item
        
    Returns:
        Result of operation
    """
    try:
        # Check if character exists
        character_result = supabase.table("characters").select("id, name, created_by").eq("id", str(character_id)).execute()
        
        if not character_result.data:
            logger.error(f"Character {character_id} not found")
            return {"success": False, "error": "Character not found"}
            
        character = character_result.data[0]
        
        # Check if inventory item exists and belongs to character
        inventory_result = supabase.table("inventory").select("*, items(*)").eq("id", str(inventory_item_id)).eq("character_id", str(character_id)).execute()
        
        if not inventory_result.data:
            logger.error(f"Inventory item {inventory_item_id} not found or does not belong to character {character_id}")
            return {"success": False, "error": "Inventory item not found"}
            
        inventory_item = inventory_result.data[0]
        item = inventory_item.get("items", {})
        
        # Check if item is equippable
        equipment_slot = item.get("equipment_slot")
        if not equipment_slot:
            logger.warning(f"Item {item.get('id')} is not equippable")
            return {"success": False, "error": "Item is not equippable"}
            
        # Check if another item is already equipped in the same slot
        existing_equipped = supabase.table("inventory").select("id").eq("character_id", str(character_id)).eq("equipped", True).execute()
        
        if existing_equipped.data:
            for equipped_item in existing_equipped.data:
                # Get the equipped item details
                equipped_details = supabase.table("inventory").select("*, items(*)").eq("id", equipped_item.get("id")).execute()
                
                if equipped_details.data:
                    equipped_slot = equipped_details.data[0].get("items", {}).get("equipment_slot")
                    
                    # If same slot, unequip the current item first
                    if equipped_slot == equipment_slot:
                        unequip_result = supabase.table("inventory").update({
                            "equipped": False,
                            "updated_at": "now()"
                        }).eq("id", equipped_item.get("id")).execute()
                        
                        if not unequip_result.data:
                            logger.error(f"Failed to unequip item {equipped_item.get('id')}")
                            return {"success": False, "error": "Failed to unequip current item"}
                            
                        logger.info(f"Unequipped item {equipped_item.get('id')} from slot {equipment_slot}")
        
        # Equip the new item
        equip_result = supabase.table("inventory").update({
            "equipped": True,
            "updated_at": "now()"
        }).eq("id", str(inventory_item_id)).execute()
        
        if not equip_result.data:
            logger.error(f"Failed to equip item {inventory_item_id}")
            return {"success": False, "error": "Failed to equip item"}
            
        # Send notification
        user_id = character.get("created_by")
        if user_id:
            await create_character_notification(
                user_id=UUID(user_id),
                character_id=character_id,
                title=f"Item Equipped: {item.get('name')}",
                message=f"{character.get('name')} equipped {item.get('name')}.",
                priority=NotificationPriority.LOW
            )
        
        return {
            "success": True,
            "inventory_item": equip_result.data[0],
            "message": f"Equipped {item.get('name')} in the {equipment_slot} slot"
        }
            
    except Exception as e:
        logger.error(f"Error equipping item: {str(e)}")
        return {"success": False, "error": str(e)}


async def unequip_item(character_id: UUID, inventory_item_id: UUID) -> Dict[str, Any]:
    """
    Unequip an item from a character.
    
    Args:
        character_id: UUID of character
        inventory_item_id: UUID of inventory item
        
    Returns:
        Result of operation
    """
    try:
        # Check if character exists
        character_result = supabase.table("characters").select("id, name").eq("id", str(character_id)).execute()
        
        if not character_result.data:
            logger.error(f"Character {character_id} not found")
            return {"success": False, "error": "Character not found"}
            
        # Check if inventory item exists, belongs to character, and is equipped
        inventory_result = supabase.table("inventory").select("*, items(*)").eq("id", str(inventory_item_id)).eq("character_id", str(character_id)).eq("equipped", True).execute()
        
        if not inventory_result.data:
            logger.error(f"Equipped inventory item {inventory_item_id} not found")
            return {"success": False, "error": "Equipped inventory item not found"}
            
        inventory_item = inventory_result.data[0]
        
        # Unequip the item
        unequip_result = supabase.table("inventory").update({
            "equipped": False,
            "updated_at": "now()"
        }).eq("id", str(inventory_item_id)).execute()
        
        if not unequip_result.data:
            logger.error(f"Failed to unequip item {inventory_item_id}")
            return {"success": False, "error": "Failed to unequip item"}
            
        return {
            "success": True,
            "inventory_item": unequip_result.data[0],
            "message": f"Unequipped {inventory_item.get('items', {}).get('name', 'item')}"
        }
            
    except Exception as e:
        logger.error(f"Error unequipping item: {str(e)}")
        return {"success": False, "error": str(e)}


async def get_character_inventory(character_id: UUID, include_item_details: bool = True) -> Dict[str, Any]:
    """
    Get a character's inventory.
    
    Args:
        character_id: UUID of character
        include_item_details: Whether to include full item details
        
    Returns:
        Character inventory data
    """
    try:
        # Check if character exists
        character_result = supabase.table("characters").select("id, name").eq("id", str(character_id)).execute()
        
        if not character_result.data:
            logger.error(f"Character {character_id} not found")
            return {"success": False, "error": "Character not found"}
            
        # Get inventory items
        if include_item_details:
            inventory_result = supabase.table("inventory").select("*, items(*)").eq("character_id", str(character_id)).execute()
        else:
            inventory_result = supabase.table("inventory").select("*").eq("character_id", str(character_id)).execute()
            
        return {
            "success": True,
            "character_id": character_id,
            "character_name": character_result.data[0].get("name"),
            "inventory": inventory_result.data
        }
            
    except Exception as e:
        logger.error(f"Error getting character inventory: {str(e)}")
        return {"success": False, "error": str(e)}


async def get_equipped_items(character_id: UUID) -> Dict[str, Any]:
    """
    Get a character's equipped items.
    
    Args:
        character_id: UUID of character
        
    Returns:
        Equipped items data
    """
    try:
        # Check if character exists
        character_result = supabase.table("characters").select("id, name").eq("id", str(character_id)).execute()
        
        if not character_result.data:
            logger.error(f"Character {character_id} not found")
            return {"success": False, "error": "Character not found"}
            
        # Get equipped items
        equipped_result = supabase.table("inventory").select("*, items(*)").eq("character_id", str(character_id)).eq("equipped", True).execute()
        
        # Organize by equipment slot
        equipped_by_slot = {}
        for item in equipped_result.data:
            slot = item.get("items", {}).get("equipment_slot")
            if slot:
                equipped_by_slot[slot] = item
                
        return {
            "success": True,
            "character_id": character_id,
            "character_name": character_result.data[0].get("name"),
            "equipped_items": equipped_by_slot,
            "raw_equipped": equipped_result.data
        }
            
    except Exception as e:
        logger.error(f"Error getting equipped items: {str(e)}")
        return {"success": False, "error": str(e)}


async def transfer_item(
    from_character_id: UUID,
    to_character_id: UUID,
    inventory_item_id: UUID,
    quantity: int = 1
) -> Dict[str, Any]:
    """
    Transfer an item between characters.
    
    Args:
        from_character_id: UUID of source character
        to_character_id: UUID of destination character
        inventory_item_id: UUID of inventory item
        quantity: Number of items to transfer
        
    Returns:
        Result of operation
    """
    try:
        # Check if characters exist
        characters_result = supabase.table("characters").select("id, name, created_by").in_("id", [str(from_character_id), str(to_character_id)]).execute()
        
        if len(characters_result.data) != 2:
            missing = []
            if not any(c.get("id") == str(from_character_id) for c in characters_result.data):
                missing.append(f"Source character {from_character_id}")
            if not any(c.get("id") == str(to_character_id) for c in characters_result.data):
                missing.append(f"Destination character {to_character_id}")
                
            logger.error(f"Characters not found: {', '.join(missing)}")
            return {"success": False, "error": f"Characters not found: {', '.join(missing)}"}
            
        # Get character details
        from_character = next((c for c in characters_result.data if c.get("id") == str(from_character_id)), None)
        to_character = next((c for c in characters_result.data if c.get("id") == str(to_character_id)), None)
        
        # Check if inventory item exists and belongs to source character
        inventory_result = supabase.table("inventory").select("*, items(*)").eq("id", str(inventory_item_id)).eq("character_id", str(from_character_id)).execute()
        
        if not inventory_result.data:
            logger.error(f"Inventory item {inventory_item_id} not found or does not belong to character {from_character_id}")
            return {"success": False, "error": "Inventory item not found"}
            
        inventory_item = inventory_result.data[0]
        current_quantity = inventory_item.get("quantity", 0)
        item = inventory_item.get("items", {})
        
        # Check if item is equipped
        if inventory_item.get("equipped", False):
            logger.warning(f"Cannot transfer equipped item {inventory_item_id}")
            return {"success": False, "error": "Cannot transfer equipped item"}
            
        # Check if have enough quantity
        if current_quantity < quantity:
            logger.warning(f"Not enough items to transfer {quantity} from inventory")
            return {"success": False, "error": f"Not enough items to transfer (have {current_quantity}, trying to transfer {quantity})"}
            
        # Remove from source inventory
        remove_result = await remove_item_from_inventory(from_character_id, UUID(inventory_item_id), quantity)
        
        if not remove_result.get("success"):
            logger.error(f"Failed to remove item from source inventory: {remove_result.get('error')}")
            return {"success": False, "error": f"Failed to remove item from source inventory: {remove_result.get('error')}"}
            
        # Add to destination inventory
        add_result = await add_item_to_inventory(
            to_character_id,
            UUID(item.get("id")),
            quantity,
            equipped=False,
            custom_name=inventory_item.get("custom_name"),
            custom_description=inventory_item.get("custom_description"),
            custom_effects=inventory_item.get("custom_effects"),
            metadata=inventory_item.get("metadata")
        )
        
        if not add_result.get("success"):
            # Try to roll back the removal
            logger.error(f"Failed to add item to destination inventory: {add_result.get('error')}")
            
            # Add the item back to source inventory
            rollback = await add_item_to_inventory(
                from_character_id,
                UUID(item.get("id")),
                quantity,
                custom_name=inventory_item.get("custom_name"),
                custom_description=inventory_item.get("custom_description"),
                custom_effects=inventory_item.get("custom_effects"),
                metadata=inventory_item.get("metadata")
            )
            
            if not rollback.get("success"):
                logger.error(f"Failed to roll back item transfer: {rollback.get('error')}")
                
            return {"success": False, "error": f"Failed to add item to destination inventory: {add_result.get('error')}"}
            
        # Create notifications for both characters
        from_user_id = from_character.get("created_by")
        to_user_id = to_character.get("created_by")
        
        if from_user_id and to_user_id:
            # Notification to source character's user
            await create_character_notification(
                user_id=UUID(from_user_id),
                character_id=from_character_id,
                title=f"Item Transferred: {item.get('name')}",
                message=f"{from_character.get('name')} gave {quantity} {item.get('name')} to {to_character.get('name')}.",
                priority=NotificationPriority.LOW
            )
            
            # Notification to destination character's user
            if from_user_id != to_user_id:  # Avoid duplicate notifications if same user
                await create_character_notification(
                    user_id=UUID(to_user_id),
                    character_id=to_character_id,
                    title=f"Item Received: {item.get('name')}",
                    message=f"{to_character.get('name')} received {quantity} {item.get('name')} from {from_character.get('name')}.",
                    priority=NotificationPriority.LOW
                )
        
        return {
            "success": True,
            "message": f"Transferred {quantity} {item.get('name')} from {from_character.get('name')} to {to_character.get('name')}"
        }
            
    except Exception as e:
        logger.error(f"Error transferring item: {str(e)}")
        return {"success": False, "error": str(e)}
