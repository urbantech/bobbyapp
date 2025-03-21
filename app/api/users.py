from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.jwt import get_current_active_user
from app.schemas.user import UserResponse
from app.database.connection import supabase
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user = Depends(get_current_active_user)):
    """Get a specific user by ID"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Only allow users to view their own information or require admin role
    if current_user["id"] != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's information"
        )
    
    user_result = supabase.table("users").select("*").eq("id", user_id).execute()
    if not user_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user_result.data[0]

@router.put("/me", response_model=UserResponse)
async def update_user(
    user_update: dict, 
    current_user = Depends(get_current_active_user)
):
    """Update current user information"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Prevent updating sensitive fields
    if "id" in user_update:
        del user_update["id"]
    if "password_hash" in user_update:
        del user_update["password_hash"]
    
    # Update user in database
    result = supabase.table("users").update(user_update).eq("id", current_user["id"]).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )
    
    updated_user = result.data[0]
    return updated_user
