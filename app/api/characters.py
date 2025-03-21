from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.jwt import get_current_active_user
from app.schemas.character import CharacterCreate, CharacterResponse, CharacterUpdate
from app.database.connection import get_supabase_client
from app.utils.character_defaults import get_default_stats, get_default_abilities, get_starter_inventory
from app.utils.ai_responses import get_character_response
from app.services.character_progression import add_experience, calculate_xp_reward
from typing import List, Dict, Any
from uuid import UUID
import logging
import datetime
import uuid

logger = logging.getLogger("app.api.characters")

router = APIRouter(prefix="/characters", tags=["characters"])

@router.post("", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    character_data: CharacterCreate,
    current_user = Depends(get_current_active_user)
):
    """Create a new AI character"""
    logger.info(f"Creating character {character_data.name} for user {current_user['id']}")
    
    # Always try to re-initialize the connection
    client = get_supabase_client()
    
    if not client:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Get default stats, abilities and inventory based on character class
    default_stats = get_default_stats(character_data.character_class)
    default_abilities = get_default_abilities(character_data.character_class)
    starter_inventory = get_starter_inventory(character_data.character_class)
    
    # Prepare character data
    now = datetime.datetime.utcnow()
    character_id = str(uuid.uuid4())
    user_id = current_user["id"]
    
    new_character = {
        "id": character_id,
        "user_id": user_id,
        "name": character_data.name,
        "character_class": character_data.character_class,
        "backstory": character_data.backstory,
        "attributes": character_data.attributes or default_stats,
        "appearance": character_data.appearance or {},
        "inventory": starter_inventory,
        "level": 1,
        "health": 100,
        "abilities": default_abilities,
        "experience": 0,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    
    # Insert character into database
    result = client.table("characters").insert(new_character)
    
    # Create a response object
    created_character = {
        "id": UUID(character_id),
        "user_id": UUID(user_id),
        "name": character_data.name,
        "character_class": character_data.character_class,
        "backstory": character_data.backstory or "",
        "attributes": character_data.attributes or default_stats,
        "appearance": character_data.appearance or {},
        "level": 1,
        "experience": 0,
        "created_at": now,
        "updated_at": now
    }
    
    return created_character

@router.get("", response_model=List[CharacterResponse])
async def get_user_characters(current_user = Depends(get_current_active_user)):
    """Get all characters created by current user"""
    logger.info(f"Getting characters for user {current_user['id']}")
    
    # Always try to re-initialize the connection
    client = get_supabase_client()
    
    if not client:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    characters = client.table("characters").select("*").eq("user_id", current_user["id"]).execute()
    return characters.data

@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: str, current_user = Depends(get_current_active_user)):
    """Get a character by ID"""
    logger.info(f"Getting character {character_id} for user {current_user['id']}")
    
    # Always try to re-initialize the connection
    client = get_supabase_client()
    
    if not client:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    result = client.table("characters").select("*").eq("id", character_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    character = result.data[0]
    
    # Check if the character belongs to the current user
    if character["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this character"
        )
    
    return character

@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: str, 
    character_update: CharacterUpdate,
    current_user = Depends(get_current_active_user)
):
    """Update a character"""
    logger.info(f"Updating character {character_id} for user {current_user['id']}")
    
    # Always try to re-initialize the connection
    client = get_supabase_client()
    
    if not client:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if character exists and user has permission
    character = client.table("characters").select("*").eq("id", character_id).execute()
    if not character.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    if character.data[0]["user_id"] != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this character"
        )
    
    # Update character in database
    update_data = character_update.dict(exclude_unset=True)
    result = client.table("characters").update(update_data).eq("id", character_id).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update character"
        )
    
    updated_character = result.data[0]
    return updated_character

@router.post("/{character_id}/interact", response_model=Dict[str, Any])
async def interact_with_character(
    character_id: str,
    interaction: Dict[str, Any],
    current_user = Depends(get_current_active_user)
):
    """Interact with a character via AI"""
    logger.info(f"Interacting with character {character_id} for user {current_user['id']}")
    
    # Always try to re-initialize the connection
    client = get_supabase_client()
    
    if not client:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if character exists
    character = client.table("characters").select("*").eq("id", character_id).execute()
    if not character.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # Get conversation history (in a real app, would fetch from database)
    # TODO: Implement conversation history retrieval
    
    # Generate response using AI utility
    character_data = character.data[0]
    ai_response = get_character_response(
        character=character_data,
        user_message=interaction.get("message")
    )
    
    return {
        "character_id": character_id,
        "response": ai_response
    }

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
    logger.info(f"Adding experience to character {character_id} for user {current_user['id']}")
    
    user_id = current_user.get("id")
    
    # Always try to re-initialize the connection
    client = get_supabase_client()
    
    if not client:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if character exists and belongs to user
    result = client.table("characters").select("*").eq("id", str(character_id)).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
    
    character = result.data[0]
    
    # Verify ownership
    if character.get("user_id") != user_id and current_user.get("role") != "admin":
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


@router.post("/{character_id}/xp-reward", response_model=Dict[str, Any])
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
    logger.info(f"Awarding XP for action on character {character_id} for user {current_user['id']}")
    
    user_id = current_user.get("id")
    
    # Always try to re-initialize the connection
    client = get_supabase_client()
    
    if not client:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if character exists and belongs to user
    result = client.table("characters").select("*").eq("id", str(character_id)).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
    
    character = result.data[0]
    
    # Verify ownership
    if character.get("user_id") != user_id and current_user.get("role") != "admin":
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


@router.get("/{character_id}/stats", response_model=Dict[str, Any])
async def get_character_stats(character_id: UUID, current_user = Depends(get_current_active_user)):
    """Get detailed stats for a character"""
    logger.info(f"Getting stats for character {character_id} for user {current_user['id']}")
    
    user_id = current_user.get("id")
    
    # Always try to re-initialize the connection
    client = get_supabase_client()
    
    if not client:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if character exists and belongs to user
    result = client.table("characters").select("*").eq("id", str(character_id)).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
    
    character = result.data[0]
    
    # Verify ownership or admin status
    if character.get("user_id") != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this character"
        )
    
    # Return detailed stats
    return {
        "character_id": character_id,
        "name": character.get("name"),
        "level": character.get("level", 1),
        "experience": character.get("experience", 0),
        "character_class": character.get("character_class"),
        "stats": character.get("stats", {}),
        "abilities": character.get("abilities", {})
    }
