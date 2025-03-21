from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.jwt import get_current_active_user
from app.schemas.quest import QuestCreate, QuestResponse, QuestUpdate
from app.database.connection import supabase
from typing import List, Dict, Any

router = APIRouter(prefix="/quests", tags=["quests"])

@router.post("", response_model=QuestResponse, status_code=status.HTTP_201_CREATED)
async def create_quest(
    quest_data: QuestCreate,
    current_user = Depends(get_current_active_user)
):
    """Create a new quest"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Create new quest
    new_quest = {
        "name": quest_data.name,
        "description": quest_data.description,
        "difficulty": quest_data.difficulty,
        "reward": quest_data.reward,
        "status": "Pending",
        "assigned_to": current_user["id"]
    }
    
    # Insert quest into database
    result = supabase.table("quests").insert(new_quest).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create quest"
        )
    
    created_quest = result.data[0]
    return created_quest

@router.get("", response_model=List[QuestResponse])
async def get_user_quests(current_user = Depends(get_current_active_user)):
    """Get all quests for current user"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Get all quests assigned to user
    quests = supabase.table("quests").select("*").eq("assigned_to", current_user["id"]).execute()
    return quests.data

@router.get("/{quest_id}", response_model=QuestResponse)
async def get_quest(quest_id: str, current_user = Depends(get_current_active_user)):
    """Get a specific quest by ID"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Get quest by ID
    quest = supabase.table("quests").select("*").eq("id", quest_id).execute()
    if not quest.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quest not found"
        )
    
    # Check if user has permission to access this quest
    if quest.data[0]["assigned_to"] != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this quest"
        )
    
    return quest.data[0]

@router.put("/{quest_id}", response_model=QuestResponse)
async def update_quest(
    quest_id: str,
    quest_update: QuestUpdate,
    current_user = Depends(get_current_active_user)
):
    """Update a quest"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if quest exists and user has permission
    quest = supabase.table("quests").select("*").eq("id", quest_id).execute()
    if not quest.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quest not found"
        )
    
    if quest.data[0]["assigned_to"] != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this quest"
        )
    
    # Update quest in database
    update_data = quest_update.dict(exclude_unset=True)
    result = supabase.table("quests").update(update_data).eq("id", quest_id).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update quest"
        )
    
    updated_quest = result.data[0]
    return updated_quest

@router.put("/{quest_id}/complete", response_model=QuestResponse)
async def complete_quest(quest_id: str, current_user = Depends(get_current_active_user)):
    """Mark a quest as completed"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if quest exists and user has permission
    quest = supabase.table("quests").select("*").eq("id", quest_id).execute()
    if not quest.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quest not found"
        )
    
    if quest.data[0]["assigned_to"] != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete this quest"
        )
    
    # Update quest status in database
    result = supabase.table("quests").update({"status": "Completed"}).eq("id", quest_id).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete quest"
        )
    
    updated_quest = result.data[0]
    return updated_quest

@router.put("/{quest_id}/fail", response_model=QuestResponse)
async def fail_quest(quest_id: str, current_user = Depends(get_current_active_user)):
    """Mark a quest as failed"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if quest exists and user has permission
    quest = supabase.table("quests").select("*").eq("id", quest_id).execute()
    if not quest.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quest not found"
        )
    
    if quest.data[0]["assigned_to"] != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to fail this quest"
        )
    
    # Update quest status in database
    result = supabase.table("quests").update({"status": "Failed"}).eq("id", quest_id).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update quest status"
        )
    
    updated_quest = result.data[0]
    return updated_quest
