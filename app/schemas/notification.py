"""
Notification schema for the application.
Handles in-game notifications and user alerts.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    """Type of notification"""
    SYSTEM = "system"  # System alerts and announcements
    QUEST = "quest"    # Quest updates and completions
    CHARACTER = "character"  # Character level ups, status changes
    MESSAGE = "message"  # New messages or conversation alerts
    FRIEND = "friend"   # Friend requests and social interactions
    ACHIEVEMENT = "achievement"  # Achievements and rewards
    DICE = "dice"      # Important dice roll results


class NotificationPriority(str, Enum):
    """Priority level of notification"""
    LOW = "low"        # Informational, non-urgent
    MEDIUM = "medium"  # Standard importance
    HIGH = "high"      # Important, attention needed
    CRITICAL = "critical"  # Urgent action required


class NotificationCreate(BaseModel):
    """Schema for creating a new notification"""
    user_id: UUID
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    related_entity_id: Optional[UUID] = None
    related_entity_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_read: bool = False
    expires_at: Optional[datetime] = None


class NotificationUpdate(BaseModel):
    """Schema for updating a notification"""
    is_read: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    id: UUID
    user_id: UUID
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority
    related_entity_id: Optional[UUID] = None
    related_entity_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_read: bool
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class NotificationBulkUpdate(BaseModel):
    """Schema for bulk updating notifications"""
    notification_ids: List[UUID]
    is_read: bool


class NotificationCount(BaseModel):
    """Count of unread notifications"""
    total: int
    high_priority: int = 0
    critical_priority: int = 0


class NotificationFilter(BaseModel):
    """Filter for querying notifications"""
    is_read: Optional[bool] = None
    notification_type: Optional[NotificationType] = None
    priority: Optional[NotificationPriority] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
