"""
Inventory schemas for the API.
Handles items, equipment, and inventory management.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from uuid import UUID
from datetime import datetime
from enum import Enum


class ItemRarity(str, Enum):
    """Rarity levels for items"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"


class ItemType(str, Enum):
    """Types of items"""
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    SCROLL = "scroll"
    QUEST = "quest"
    MATERIAL = "material"
    FOOD = "food"
    CONTAINER = "container"
    MISC = "misc"


class EquipmentSlot(str, Enum):
    """Equipment slots for character gear"""
    HEAD = "head"
    NECK = "neck"
    CHEST = "chest"
    BACK = "back"
    HANDS = "hands"
    WAIST = "waist"
    LEGS = "legs"
    FEET = "feet"
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    FINGER_1 = "finger_1"
    FINGER_2 = "finger_2"
    TRINKET_1 = "trinket_1"
    TRINKET_2 = "trinket_2"


class ItemEffectType(str, Enum):
    """Types of effects items can have"""
    STAT_BOOST = "stat_boost"
    DOT = "damage_over_time"
    HOT = "heal_over_time"
    BUFF = "buff"
    DEBUFF = "debuff"
    SPECIAL = "special"


class ItemCreate(BaseModel):
    """Schema for creating a new item"""
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=5)
    item_type: ItemType
    rarity: ItemRarity = ItemRarity.COMMON
    value: int = Field(0, ge=0)
    weight: float = Field(0.0, ge=0.0)
    stackable: bool = False
    max_stack: Optional[int] = Field(1, ge=1)
    effects: Optional[List[Dict[str, Any]]] = None
    requirements: Optional[Dict[str, Any]] = None
    equipment_slot: Optional[EquipmentSlot] = None
    stats: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None


class ItemResponse(ItemCreate):
    """Schema for item response"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class InventoryItemBase(BaseModel):
    """Base schema for inventory items"""
    item_id: UUID
    quantity: int = Field(1, ge=1)
    equipped: bool = False
    durability: Optional[int] = None
    custom_name: Optional[str] = None
    custom_description: Optional[str] = None
    custom_effects: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class InventoryItemCreate(InventoryItemBase):
    """Schema for adding an item to inventory"""
    character_id: UUID


class InventoryItemResponse(InventoryItemBase):
    """Schema for inventory item response with item details"""
    id: UUID
    character_id: UUID
    item: ItemResponse
    created_at: datetime
    updated_at: Optional[datetime] = None


class InventoryUpdate(BaseModel):
    """Schema for updating inventory"""
    items_to_add: Optional[List[Dict[str, Any]]] = None
    items_to_remove: Optional[List[UUID]] = None
    items_to_update: Optional[List[Dict[str, Any]]] = None


class InventoryTransfer(BaseModel):
    """Schema for transferring items between characters"""
    from_character_id: UUID
    to_character_id: UUID
    items: List[Dict[str, Any]]


class InventoryEquipRequest(BaseModel):
    """Schema for equipping/unequipping items"""
    inventory_item_id: UUID
    equip: bool = True


class CraftingRecipe(BaseModel):
    """Schema for crafting recipes"""
    id: UUID
    name: str
    description: str
    skill_required: Optional[str] = None
    skill_level: Optional[int] = None
    materials: List[Dict[str, Any]]
    result_item_id: UUID
    result_quantity: int = 1
    crafting_time: int  # in seconds
    metadata: Optional[Dict[str, Any]] = None


class CraftingRequest(BaseModel):
    """Schema for crafting request"""
    recipe_id: UUID
    character_id: UUID
    quantity: int = 1
