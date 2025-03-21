"""
Admin API for managing the RPG platform.
Access to these endpoints is restricted to admin users.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.auth.jwt import get_current_active_user
from app.database.connection import supabase
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/admin", tags=["admin"])

# Admin-only dependency
async def get_current_admin(current_user = Depends(get_current_active_user)):
    """Verify the user has admin privileges"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

@router.get("/stats", response_model=Dict[str, Any])
async def get_system_stats(admin = Depends(get_current_admin)):
    """Get system statistics and metrics"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Get user count
    users_result = supabase.table("users").select("count", count="exact").execute()
    user_count = users_result.count if hasattr(users_result, "count") else 0
    
    # Get character count
    characters_result = supabase.table("characters").select("count", count="exact").execute()
    character_count = characters_result.count if hasattr(characters_result, "count") else 0
    
    # Get conversation count
    conversations_result = supabase.table("conversations").select("count", count="exact").execute()
    conversation_count = conversations_result.count if hasattr(conversations_result, "count") else 0
    
    # Get message count
    messages_result = supabase.table("messages").select("count", count="exact").execute()
    message_count = messages_result.count if hasattr(messages_result, "count") else 0
    
    # Get quest count
    quests_result = supabase.table("quests").select("count", count="exact").execute()
    quest_count = quests_result.count if hasattr(quests_result, "count") else 0
    
    return {
        "users": user_count,
        "characters": character_count,
        "conversations": conversation_count,
        "messages": message_count,
        "quests": quest_count,
        "system_status": "healthy"
    }

@router.get("/users", response_model=List[Dict[str, Any]])
async def get_all_users(
    admin = Depends(get_current_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get all users with pagination"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    users = supabase.table("users").select("*").range(skip, skip + limit - 1).execute()
    return users.data

@router.get("/users/{user_id}", response_model=Dict[str, Any])
async def get_user_detail(user_id: str, admin = Depends(get_current_admin)):
    """Get detailed information about a specific user"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    user = supabase.table("users").select("*").eq("id", user_id).execute()
    if not user.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user's characters
    characters = supabase.table("characters").select("*").eq("created_by", user_id).execute()
    
    # Get user's conversations
    conversations = supabase.table("conversations").select("*").eq("user_id", user_id).execute()
    
    # Get user's quests
    quests = supabase.table("quests").select("*").eq("assigned_to", user_id).execute()
    
    return {
        "user": user.data[0],
        "characters": characters.data,
        "conversations": conversations.data,
        "quests": quests.data
    }

@router.put("/users/{user_id}/role", response_model=Dict[str, Any])
async def update_user_role(
    user_id: str, 
    role_data: Dict[str, str],
    admin = Depends(get_current_admin)
):
    """Update a user's role"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Validate role
    valid_roles = ["user", "moderator", "admin"]
    if role_data.get("role") not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Update user's role
    result = supabase.table("users").update({"role": role_data["role"]}).eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return result.data[0]

@router.get("/characters", response_model=List[Dict[str, Any]])
async def get_all_characters(
    admin = Depends(get_current_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    character_class: Optional[str] = None
):
    """Get all characters with optional filtering and pagination"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    query = supabase.table("characters").select("*")
    
    # Apply class filter if provided
    if character_class:
        query = query.eq("character_class", character_class)
    
    # Apply pagination
    result = query.range(skip, skip + limit - 1).execute()
    return result.data

@router.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(character_id: str, admin = Depends(get_current_admin)):
    """Delete a character (admin only)"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if character exists
    character = supabase.table("characters").select("*").eq("id", character_id).execute()
    if not character.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # Delete related conversations first
    conversations = supabase.table("conversations").select("id").eq("character_id", character_id).execute()
    if conversations.data:
        for conv in conversations.data:
            # Delete messages for each conversation
            supabase.table("messages").delete().eq("conversation_id", conv["id"]).execute()
            
            # Delete multimodal data for each conversation
            supabase.table("multimodal_data").delete().eq("conversation_id", conv["id"]).execute()
        
        # Delete conversations
        supabase.table("conversations").delete().eq("character_id", character_id).execute()
    
    # Delete character
    supabase.table("characters").delete().eq("id", character_id).execute()
    
    return None

@router.get("/system/health", response_model=Dict[str, Any])
async def detailed_health_check(admin = Depends(get_current_admin)):
    """Get detailed system health information"""
    # Check database connection
    db_connected = supabase is not None
    db_status = "connected" if db_connected else "disconnected"
    
    # Memory usage
    import psutil
    memory = psutil.virtual_memory()
    
    return {
        "database": {
            "status": db_status,
            "connected": db_connected
        },
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent
        },
        "status": "healthy",
        "timestamp": str(import_time())
    }

def import_time():
    """Get current time for health check"""
    from datetime import datetime
    return datetime.utcnow()
