from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    sender_type: Literal["user", "character"]

class MessageResponse(MessageBase):
    sender_id: str
    sender_type: str
    content: str
    timestamp: datetime
    conversation_id: Optional[str] = None
    
    class Config:
        orm_mode = True

class ConversationBase(BaseModel):
    character_id: str

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(ConversationBase):
    id: str
    user_id: str
    messages: List[Dict[str, Any]] = []
    created_at: datetime
    
    class Config:
        orm_mode = True
