"""
Notification service for managing notifications across the application.
"""

import logging
from datetime import datetime, timedelta
from uuid import UUID
from typing import Dict, Any, Optional

from app.database.connection import supabase
from app.schemas.notification import NotificationType, NotificationPriority

logger = logging.getLogger(__name__)


async def create_notification(
    user_id: UUID,
    title: str,
    message: str,
    notification_type: NotificationType,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    related_entity_id: Optional[UUID] = None,
    related_entity_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    expires_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Create a notification for a user.
    
    Args:
        user_id: The ID of the user to receive the notification
        title: Short, descriptive title for the notification
        message: Detailed message content
        notification_type: Type of notification (system, quest, etc.)
        priority: Priority level (low, medium, high, critical)
        related_entity_id: Optional ID of related entity (quest, character, etc.)
        related_entity_type: Optional type of related entity
        metadata: Optional additional data for the notification
        expires_at: Optional expiration date for the notification
    
    Returns:
        The created notification data
    """
    try:
        now = datetime.utcnow()
        
        notification_data = {
            "user_id": str(user_id),
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "priority": priority,
            "created_at": now,
            "updated_at": now,
            "is_read": False
        }
        
        if related_entity_id:
            notification_data["related_entity_id"] = str(related_entity_id)
        
        if related_entity_type:
            notification_data["related_entity_type"] = related_entity_type
        
        if metadata:
            notification_data["metadata"] = metadata
        
        if expires_at:
            notification_data["expires_at"] = expires_at
        
        # Insert into database
        result = supabase.table("notifications").insert(notification_data).execute()
        
        if not result.data:
            logger.error(f"Failed to create notification for user {user_id}")
            return None
        
        logger.info(f"Created {priority} priority {notification_type} notification for user {user_id}")
        return result.data[0]
    
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        return None


async def create_system_notification(
    user_id: UUID,
    title: str,
    message: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a system notification for a user.
    
    Args:
        user_id: The ID of the user to receive the notification
        title: Short, descriptive title for the notification
        message: Detailed message content
        priority: Priority level
        metadata: Optional additional data
    
    Returns:
        The created notification data
    """
    return await create_notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=NotificationType.SYSTEM,
        priority=priority,
        metadata=metadata
    )


async def create_quest_notification(
    user_id: UUID,
    quest_id: UUID,
    title: str,
    message: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM
) -> Dict[str, Any]:
    """
    Create a quest-related notification for a user.
    
    Args:
        user_id: The ID of the user to receive the notification
        quest_id: The ID of the related quest
        title: Short, descriptive title for the notification
        message: Detailed message content
        priority: Priority level
    
    Returns:
        The created notification data
    """
    return await create_notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=NotificationType.QUEST,
        priority=priority,
        related_entity_id=quest_id,
        related_entity_type="quest"
    )


async def create_character_notification(
    user_id: UUID,
    character_id: UUID,
    title: str,
    message: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM
) -> Dict[str, Any]:
    """
    Create a character-related notification for a user.
    
    Args:
        user_id: The ID of the user to receive the notification
        character_id: The ID of the related character
        title: Short, descriptive title for the notification
        message: Detailed message content
        priority: Priority level
    
    Returns:
        The created notification data
    """
    return await create_notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=NotificationType.CHARACTER,
        priority=priority,
        related_entity_id=character_id,
        related_entity_type="character"
    )


async def create_message_notification(
    user_id: UUID,
    conversation_id: UUID,
    title: str,
    message: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM
) -> Dict[str, Any]:
    """
    Create a message-related notification for a user.
    
    Args:
        user_id: The ID of the user to receive the notification
        conversation_id: The ID of the related conversation
        title: Short, descriptive title for the notification
        message: Detailed message content
        priority: Priority level
    
    Returns:
        The created notification data
    """
    return await create_notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=NotificationType.MESSAGE,
        priority=priority,
        related_entity_id=conversation_id,
        related_entity_type="conversation"
    )


async def create_achievement_notification(
    user_id: UUID,
    achievement_name: str,
    description: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create an achievement notification for a user.
    
    Args:
        user_id: The ID of the user to receive the notification
        achievement_name: Name of the achievement
        description: Description of the achievement
        priority: Priority level
        metadata: Optional additional data about the achievement
    
    Returns:
        The created notification data
    """
    title = f"Achievement Unlocked: {achievement_name}"
    
    return await create_notification(
        user_id=user_id,
        title=title,
        message=description,
        notification_type=NotificationType.ACHIEVEMENT,
        priority=priority,
        metadata=metadata or {"achievement": achievement_name}
    )


async def create_dice_notification(
    user_id: UUID,
    dice_roll_id: UUID,
    roll_type: str,
    roll_result: int,
    context: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM
) -> Dict[str, Any]:
    """
    Create a notification for an important dice roll.
    
    Args:
        user_id: The ID of the user to receive the notification
        dice_roll_id: The ID of the related dice roll
        roll_type: Type of dice roll (e.g., "attack", "skill check")
        roll_result: The result of the roll
        context: Context of the roll
        priority: Priority level
    
    Returns:
        The created notification data
    """
    title = f"Dice Roll: {roll_type.capitalize()}"
    message = f"Your {roll_type} roll resulted in {roll_result}. {context}"
    
    return await create_notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=NotificationType.DICE,
        priority=priority,
        related_entity_id=dice_roll_id,
        related_entity_type="dice_roll",
        metadata={"roll_type": roll_type, "result": roll_result}
    )


async def mark_notifications_as_read(user_id: UUID, notification_ids: list[UUID]) -> int:
    """
    Mark multiple notifications as read.
    
    Args:
        user_id: The ID of the user
        notification_ids: List of notification IDs to mark as read
    
    Returns:
        Number of notifications updated
    """
    try:
        str_ids = [str(id) for id in notification_ids]
        
        result = supabase.table("notifications").update({
            "is_read": True,
            "updated_at": datetime.utcnow()
        }).in_("id", str_ids).eq("user_id", str(user_id)).execute()
        
        return len(result.data)
    
    except Exception as e:
        logger.error(f"Error marking notifications as read: {str(e)}")
        return 0


async def delete_expired_notifications() -> int:
    """
    Delete all expired notifications.
    Should be run periodically as a scheduled task.
    
    Returns:
        Number of notifications deleted
    """
    try:
        now = datetime.utcnow()
        
        result = supabase.table("notifications").delete().lt("expires_at", now).execute()
        
        count = len(result.data)
        logger.info(f"Deleted {count} expired notifications")
        return count
    
    except Exception as e:
        logger.error(f"Error deleting expired notifications: {str(e)}")
        return 0
