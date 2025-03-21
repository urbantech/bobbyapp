from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
import uuid
from app.models.base import BaseDBModel

class QuestStatus(str, Literal["Pending", "Completed", "Failed"]):
    pass

class Quest(BaseDBModel):
    """Quest model for roleplaying adventures"""
    name: str
    description: str
    difficulty: str  # easy, medium, hard
    reward: Dict[str, Any]  # JSONB in Supabase
    status: QuestStatus = "Pending"
    assigned_to: str  # User ID (Foreign Key)
    
    # Methods to implement from datamodel.md
    def start_quest(self) -> Dict[str, Any]:
        """Initialize and start the quest"""
        # Logic to begin a quest
        return {"status": "started", "quest_id": self.id}
    
    def complete_quest(self) -> Dict[str, Any]:
        """Mark quest as completed and distribute rewards"""
        self.status = "Completed"
        # Logic to handle rewards
        return {"status": "completed", "rewards": self.reward}
    
    def fail_quest(self, reason: str = None) -> Dict[str, Any]:
        """Mark quest as failed"""
        self.status = "Failed"
        return {"status": "failed", "reason": reason}
