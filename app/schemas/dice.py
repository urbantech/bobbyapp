from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DiceRollBase(BaseModel):
    dice_type: int  # e.g., 20 for D20, 6 for D6
    character_id: Optional[str] = None  # Optional association with a character

class DiceRollCreate(DiceRollBase):
    pass

class DiceRollResponse(DiceRollBase):
    id: str
    user_id: str
    result: int
    created_at: datetime
    
    class Config:
        orm_mode = True
