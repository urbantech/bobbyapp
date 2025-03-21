from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.jwt import get_current_active_user
from app.schemas.dice import DiceRollCreate, DiceRollResponse
from app.database.connection import supabase
from typing import List
import random

router = APIRouter(prefix="/dice", tags=["dice rolls"])

@router.post("", response_model=DiceRollResponse, status_code=status.HTTP_201_CREATED)
async def roll_dice(
    dice_data: DiceRollCreate,
    current_user = Depends(get_current_active_user)
):
    """Roll a dice and store the result"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Validate dice type
    if dice_data.dice_type <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dice type must be a positive integer"
        )
    
    # If character_id is provided, check if it exists and user has access
    if dice_data.character_id:
        character = supabase.table("characters").select("*").eq("id", dice_data.character_id).execute()
        if not character.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Character not found"
            )
        
        if character.data[0]["created_by"] != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to roll dice for this character"
            )
    
    # Roll the dice
    result = random.randint(1, dice_data.dice_type)
    
    # Create dice roll record
    new_dice_roll = {
        "user_id": current_user["id"],
        "character_id": dice_data.character_id,
        "dice_type": dice_data.dice_type,
        "result": result
    }
    
    # Insert dice roll into database
    db_result = supabase.table("dice_rolls").insert(new_dice_roll).execute()
    if not db_result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record dice roll"
        )
    
    created_roll = db_result.data[0]
    return created_roll

@router.get("", response_model=List[DiceRollResponse])
async def get_user_dice_rolls(current_user = Depends(get_current_active_user)):
    """Get all dice rolls for current user"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Get all dice rolls for user
    dice_rolls = supabase.table("dice_rolls").select("*").eq("user_id", current_user["id"]).execute()
    return dice_rolls.data

@router.get("/character/{character_id}", response_model=List[DiceRollResponse])
async def get_character_dice_rolls(
    character_id: str,
    current_user = Depends(get_current_active_user)
):
    """Get all dice rolls for a specific character"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if character exists and user has permission
    character = supabase.table("characters").select("*").eq("id", character_id).execute()
    if not character.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    if character.data[0]["created_by"] != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access dice rolls for this character"
        )
    
    # Get all dice rolls for character
    dice_rolls = supabase.table("dice_rolls").select("*").eq("character_id", character_id).execute()
    return dice_rolls.data
