from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from app.models.base import BaseDBModel

class User(BaseDBModel):
    """User model for storing user related details"""
    username: str
    email: str
    password_hash: str
    subscription_level: str = "free"  # free, premium, pro
    
    # Methods to implement from datamodel.md
    def create_character(self, character_data: Dict[str, Any]):
        """Create a new character for the user"""
        pass
    
    def interact_with_character(self, character_id: str, message: str):
        """Interact with a character"""
        pass
    
    def roll_dice(self, dice_type: int, modifier: int = 0):
        """Roll a dice with optional modifier"""
        pass
    
    def start_quest(self, quest_name: str, difficulty: str = "medium"):
        """Start a new quest"""
        pass
