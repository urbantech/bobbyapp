from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum

class MediaType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MODEL_3D = "3d_model"
    OTHER = "other"

class MultiModalDataBase(BaseModel):
    conversation_id: str
    type: MediaType
    content_url: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MultiModalDataCreate(MultiModalDataBase):
    pass

class MultiModalDataResponse(MultiModalDataBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class MultiModalDataUpdate(BaseModel):
    type: Optional[MediaType] = None
    content_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
