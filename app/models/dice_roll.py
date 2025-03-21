from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from app.models.base import BaseDBModel
import random

class DiceRoll(BaseDBModel):
    """Dice roll model for RPG mechanics"""
    user_id: str  # Foreign Key to User
    character_id: Optional[str] = None  # Optional Foreign Key to Character
    dice_type: int  # e.g., 20 for D20, 6 for D6
    result: Optional[int] = None
    
    # Methods to implement from datamodel.md
    def roll_dice(self) -> int:
        """Roll the dice and return result"""
        if self.dice_type <= 0:
            raise ValueError("Dice type must be a positive integer")
            
        result = random.randint(1, self.dice_type)
        self.result = result
        return result
    
    def validate_roll(self) -> bool:
        """Validate that a dice roll is legitimate"""
        # In a real implementation, this might include cheat detection
        return 1 <= self.result <= self.dice_type if self.result is not None else False
