"""
API routes for character progression system.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import Dict, Any, List, Optional
from uuid import UUID

from app.schemas.character import (
    ExperienceResponse,
    LevelUpData,
    CharacterStats
)
from app.auth.jwt import get_current_active_user, get_current_admin_user
from app.database.connection import supabase
from app.services.character_progression import (
    add_experience,
    calculate_xp_reward
)

router = APIRouter(prefix="/character-progression", tags=["character progression"])


@router.post("/{character_id}/experience", response_model=Dict[str, Any])
async def add_character_experience(
    character_id: UUID, 
    xp_data: Dict[str, Any],
    current_user = Depends(get_current_active_user)
):
    """
    Add experience points to a character, potentially triggering level ups.
    
    Example request body:
    ```json
    {
        "xp_amount": 100
    }
    ```
    """
    user_id = current_user.get("id")
    
    # Check if character exists and belongs to user
    result = supabase.table("characters").select("*").eq("id", str(character_id)).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
    
    character = result.data[0]
    
    # Verify ownership
    if character.get("created_by") != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this character"
        )
    
    # Get XP amount from request
    xp_amount = xp_data.get("xp_amount", 0)
    
    if xp_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="XP amount must be greater than 0"
        )
    
    # Add experience and handle level ups
    result = await add_experience(character_id, xp_amount)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to add experience")
        )
    
    return result


@router.post("/{character_id}/reward", response_model=Dict[str, Any])
async def add_action_reward(
    character_id: UUID,
    reward_data: Dict[str, Any],
    current_user = Depends(get_current_active_user)
):
    """
    Calculate and award XP for an action.
    
    Example request body:
    ```json
    {
        "action_type": "combat",
        "difficulty": "hard",
        "success": true
    }
    ```
    """
    user_id = current_user.get("id")
    
    # Check if character exists and belongs to user
    result = supabase.table("characters").select("*").eq("id", str(character_id)).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
    
    character = result.data[0]
    
    # Verify ownership
    if character.get("created_by") != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this character"
        )
    
    # Extract data
    action_type = reward_data.get("action_type")
    difficulty = reward_data.get("difficulty", "medium")
    success = reward_data.get("success", True)
    
    if not action_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="action_type is required"
        )
    
    # Calculate XP reward
    xp_amount = await calculate_xp_reward(action_type, difficulty, success)
    
    # Add the experience
    result = await add_experience(character_id, xp_amount)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to add experience")
        )
    
    # Add the action details to the response
    result["action"] = {
        "type": action_type,
        "difficulty": difficulty,
        "success": success,
        "xp_awarded": xp_amount
    }
    
    return result


@router.get("/{character_id}/next-level", response_model=Dict[str, Any])
async def get_next_level_info(character_id: UUID, current_user = Depends(get_current_active_user)):
    """Get information about the next level for a character"""
    user_id = current_user.get("id")
    
    # Check if character exists and belongs to user
    result = supabase.table("characters").select("*").eq("id", str(character_id)).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
    
    character = result.data[0]
    
    # Verify ownership
    if character.get("created_by") != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this character's information"
        )
    
    current_level = character.get("level", 1)
    current_xp = character.get("experience", 0)
    character_class = character.get("character_class", "warrior")
    
    # Import the level requirements from the service
    from app.services.character_progression import LEVEL_XP_REQUIREMENTS, CLASS_LEVEL_BONUSES
    
    # Get next level data
    next_level = current_level + 1
    xp_for_next_level = LEVEL_XP_REQUIREMENTS.get(next_level, float('inf'))
    xp_needed = max(0, xp_for_next_level - current_xp)
    
    # Get level bonuses if available
    level_bonuses = CLASS_LEVEL_BONUSES.get(character_class.lower(), {}).get(next_level, {})
    
    return {
        "character_id": character_id,
        "character_name": character.get("name"),
        "current_level": current_level,
        "next_level": next_level,
        "current_xp": current_xp,
        "xp_for_next_level": xp_for_next_level,
        "xp_needed": xp_needed,
        "progress_percentage": min(100, (current_xp / xp_for_next_level * 100) if xp_for_next_level > 0 else 100),
        "level_bonuses": level_bonuses
    }


@router.get("/{character_id}/levels", response_model=Dict[str, Any])
async def get_level_requirements(character_id: UUID, current_user = Depends(get_current_active_user)):
    """Get all level requirements and potential bonuses for a character"""
    user_id = current_user.get("id")
    
    # Check if character exists and belongs to user
    result = supabase.table("characters").select("*").eq("id", str(character_id)).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
    
    character = result.data[0]
    
    # Verify ownership
    if character.get("created_by") != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this character's information"
        )
    
    character_class = character.get("character_class", "warrior")
    
    # Import the level requirements from the service
    from app.services.character_progression import LEVEL_XP_REQUIREMENTS, CLASS_LEVEL_BONUSES
    
    # Get class-specific bonuses
    class_bonuses = CLASS_LEVEL_BONUSES.get(character_class.lower(), {})
    
    return {
        "character_id": character_id,
        "character_name": character.get("name"),
        "character_class": character_class,
        "current_level": character.get("level", 1),
        "current_xp": character.get("experience", 0),
        "level_requirements": LEVEL_XP_REQUIREMENTS,
        "class_level_bonuses": class_bonuses
    }
