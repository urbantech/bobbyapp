"""
Character schemas for the API.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class CharacterClass(str, Enum):
    """Character class types"""
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    CLERIC = "cleric"
    RANGER = "ranger"


class CharacterBase(BaseModel):
    """Base schema for characters"""
    name: str = Field(..., min_length=2, max_length=50)
    character_class: str
    backstory: Optional[str] = None


class CharacterCreate(CharacterBase):
    """Schema for creating a new character"""
    attributes: Optional[Dict[str, Any]] = None
    appearance: Optional[Dict[str, Any]] = None


class CharacterUpdate(BaseModel):
    """Schema for updating a character"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    backstory: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    appearance: Optional[Dict[str, Any]] = None
    level: Optional[int] = Field(None, ge=1)
    experience: Optional[int] = Field(None, ge=0)


class CharacterResponse(CharacterBase):
    """Schema for character response"""
    id: UUID
    user_id: UUID
    attributes: Dict[str, Any]
    appearance: Optional[Dict[str, Any]] = None
    level: int = 1
    experience: int = 0
    created_at: datetime
    updated_at: datetime


class CharacterList(BaseModel):
    """Schema for list of characters"""
    characters: List[CharacterResponse]
    total: int


class LevelUpData(BaseModel):
    """Schema for level up data"""
    level: int
    stat_increases: Dict[str, int]
    new_ability: Optional[str] = None
    new_stats: Dict[str, Any]
    new_abilities: Dict[str, Any]


class ExperienceResponse(BaseModel):
    """Schema for experience response"""
    success: bool
    character: CharacterResponse
    xp_gained: int
    xp_total: int
    previous_level: int
    new_level: int
    level_ups: Optional[List[LevelUpData]] = None
    error: Optional[str] = None


class AbilityDetail(BaseModel):
    """Schema for ability details"""
    name: str
    description: str
    level_acquired: int
    cooldown: Optional[int] = None
    damage: Optional[int] = None
    healing: Optional[int] = None
    effect: Optional[str] = None
    duration: Optional[int] = None
    cost: Optional[Dict[str, int]] = None


class CharacterStats(BaseModel):
    """Schema for detailed character stats"""
    character_id: UUID
    name: str
    level: int
    experience: int
    character_class: str
    stats: Dict[str, Any]
    abilities: Dict[str, Any]
