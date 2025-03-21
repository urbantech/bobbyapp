from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import uuid
from app.models.base import BaseDBModel

class Character(BaseDBModel):
    """Character model for AI characters in the platform"""
    name: str
    character_class: str  # Using character_class instead of 'class' which is a Python keyword
    backstory: str
    personality: Dict[str, Any]  # JSONB in Supabase
    stats: Dict[str, int]  # JSONB in Supabase
    inventory: List[Dict[str, Any]] = []  # JSONB in Supabase
    level: int = 1
    health: int = 100
    abilities: Dict[str, Any] = {}  # JSONB in Supabase
    created_by: str  # User ID (Foreign Key)
    
    # Methods to implement from datamodel.md
    def respond_to_user(self, message: str) -> str:
        """Generate a character response to user message"""
        pass
    
    def engage_in_conversation(self, participants: List[str], context: Dict[str, Any] = None) -> str:
        """Participate in multi-character conversation"""
        pass
    
    def participate_in_combat(self, opponent_id: str, action: str, dice_roll: int = None) -> Dict[str, Any]:
        """Handle character combat actions"""
        pass
    
    def remember_past_interactions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve past interactions with a user"""
        pass
