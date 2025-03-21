"""
Notification API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timedelta

from app.schemas.notification import (
    NotificationCreate, 
    NotificationUpdate,
    NotificationResponse,
    NotificationBulkUpdate,
    NotificationCount,
    NotificationType,
    NotificationPriority,
    NotificationFilter
)
from app.auth.jwt import get_current_active_user
from app.database.connection import supabase

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(notification: NotificationCreate, current_user = Depends(get_current_active_user)):
    """
    Create a new notification.
    Admin or system-level endpoint - users can only receive notifications, not create them directly.
    """
    # Check if user is admin or system
    if current_user.get("role") not in ["admin", "system"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or system can create notifications"
        )
    
    now = datetime.utcnow()
    notification_data = notification.model_dump()
    
    # Add timestamps
    notification_data["created_at"] = now
    notification_data["updated_at"] = now
    
    # Insert into database
    result = supabase.table("notifications").insert(notification_data).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification"
        )
    
    return result.data[0]


@router.get("", response_model=List[NotificationResponse])
async def get_user_notifications(
    current_user = Depends(get_current_active_user),
    is_read: Optional[bool] = None,
    notification_type: Optional[NotificationType] = None,
    priority: Optional[NotificationPriority] = None, 
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get notifications for the current user with optional filtering.
    """
    user_id = current_user.get("id")
    
    # Start building the query
    query = supabase.table("notifications").select("*").eq("user_id", user_id)
    
    # Apply filters if provided
    if is_read is not None:
        query = query.eq("is_read", is_read)
    
    if notification_type:
        query = query.eq("notification_type", notification_type)
    
    if priority:
        query = query.eq("priority", priority)
    
    # Apply pagination
    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
    
    if not result.data:
        return []
    
    return result.data


@router.get("/count", response_model=NotificationCount)
async def get_notification_count(current_user = Depends(get_current_active_user)):
    """
    Get count of unread notifications for the current user.
    """
    user_id = current_user.get("id")
    
    # Get total unread count
    total_query = supabase.table("notifications").select("count", count="exact").eq("user_id", user_id).eq("is_read", False).execute()
    total = total_query.count if hasattr(total_query, "count") else 0
    
    # Get high priority unread count
    high_query = supabase.table("notifications").select("count", count="exact").eq("user_id", user_id).eq("is_read", False).eq("priority", NotificationPriority.HIGH).execute()
    high_priority = high_query.count if hasattr(high_query, "count") else 0
    
    # Get critical priority unread count
    critical_query = supabase.table("notifications").select("count", count="exact").eq("user_id", user_id).eq("is_read", False).eq("priority", NotificationPriority.CRITICAL).execute()
    critical_priority = critical_query.count if hasattr(critical_query, "count") else 0
    
    return {
        "total": total,
        "high_priority": high_priority,
        "critical_priority": critical_priority
    }


@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: UUID,
    notification_update: NotificationUpdate,
    current_user = Depends(get_current_active_user)
):
    """
    Update a notification (mark as read/unread).
    """
    user_id = current_user.get("id")
    
    # Check if notification exists and belongs to the user
    existing = supabase.table("notifications").select("*").eq("id", str(notification_id)).eq("user_id", user_id).execute()
    
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
    
    # Update the notification
    update_data = notification_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    result = supabase.table("notifications").update(update_data).eq("id", str(notification_id)).execute()
    
    return result.data[0]


@router.put("/bulk-update", response_model=dict)
async def bulk_update_notifications(
    update_data: NotificationBulkUpdate,
    current_user = Depends(get_current_active_user)
):
    """
    Bulk update notifications (mark multiple as read/unread).
    """
    user_id = current_user.get("id")
    notification_ids = [str(id) for id in update_data.notification_ids]
    
    # Update all notifications that belong to the user
    result = supabase.table("notifications").update({
        "is_read": update_data.is_read,
        "updated_at": datetime.utcnow()
    }).in_("id", notification_ids).eq("user_id", user_id).execute()
    
    return {"updated_count": len(result.data)}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id: UUID, current_user = Depends(get_current_active_user)):
    """
    Delete a notification.
    """
    user_id = current_user.get("id")
    
    # Check if notification exists and belongs to the user
    existing = supabase.table("notifications").select("*").eq("id", str(notification_id)).eq("user_id", user_id).execute()
    
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
    
    # Delete the notification
    supabase.table("notifications").delete().eq("id", str(notification_id)).execute()
    
    return None


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_read_notifications(current_user = Depends(get_current_active_user)):
    """
    Delete all read notifications for the current user.
    """
    user_id = current_user.get("id")
    
    # Delete all read notifications for the user
    supabase.table("notifications").delete().eq("user_id", user_id).eq("is_read", True).execute()
    
    return None
