from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from app.models.base import BaseDBModel

class Message(BaseModel):
    """Individual message in a conversation"""
    sender_id: str  # User ID or Character ID
    sender_type: str  # "user" or "character"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
class Conversation(BaseDBModel):
    """Conversation model for storing dialogue between users and characters"""
    user_id: str  # Foreign Key to User
    character_id: str  # Foreign Key to Character
    messages: List[Message] = []  # JSONB in Supabase
    
    # Methods to implement from datamodel.md
    def add_message(self, sender_id: str, sender_type: str, content: str) -> Message:
        """Add a new message to the conversation"""
        new_message = Message(
            sender_id=sender_id,
            sender_type=sender_type,
            content=content
        )
        self.messages.append(new_message)
        return new_message
    
    def retrieve_context(self, message_count: int = 10) -> List[Message]:
        """Get recent messages for context"""
        return self.messages[-message_count:] if self.messages else []
    
    def analyze_tone(self) -> Dict[str, Any]:
        """Analyze the tone of the conversation"""
        # This would use sentiment analysis or similar AI techniques
        pass
