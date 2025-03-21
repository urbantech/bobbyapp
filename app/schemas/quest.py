from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class QuestStatus(str, Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"

class QuestBase(BaseModel):
    name: str
    description: str
    difficulty: str = "medium"  # easy, medium, hard
    reward: Dict[str, Any]

class QuestCreate(QuestBase):
    pass

class QuestUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    reward: Optional[Dict[str, Any]] = None
    status: Optional[QuestStatus] = None

class QuestResponse(QuestBase):
    id: str
    status: QuestStatus
    assigned_to: str
    created_at: datetime
    
    class Config:
        orm_mode = True
