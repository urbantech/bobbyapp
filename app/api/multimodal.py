from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from app.auth.jwt import get_current_active_user
from app.schemas.multimodal import MultiModalDataCreate, MultiModalDataResponse, MultiModalDataUpdate
from app.database.connection import supabase
from typing import List, Dict, Any
import uuid
import os
from datetime import datetime

router = APIRouter(prefix="/multimodal", tags=["multimodal data"])

@router.post("", response_model=MultiModalDataResponse, status_code=status.HTTP_201_CREATED)
async def create_multimodal_data(
    data: MultiModalDataCreate,
    current_user = Depends(get_current_active_user)
):
    """Create a new multimodal data entry"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if the conversation exists and user has access
    conversation = supabase.table("conversations").select("*").eq("id", data.conversation_id).execute()
    if not conversation.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Verify user has permission for this conversation
    if conversation.data[0]["user_id"] != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add data to this conversation"
        )
    
    # Create new multimodal data entry
    new_data = {
        "conversation_id": data.conversation_id,
        "type": data.type,
        "content_url": data.content_url,
        "metadata": data.metadata
    }
    
    # Insert into database
    result = supabase.table("multimodal_data").insert(new_data).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create multimodal data entry"
        )
    
    created_data = result.data[0]
    return created_data

@router.post("/upload", response_model=Dict[str, Any])
async def upload_file(
    conversation_id: str,
    file: UploadFile = File(...),
    current_user = Depends(get_current_active_user)
):
    """Upload a file and store metadata"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if the conversation exists and user has access
    conversation = supabase.table("conversations").select("*").eq("id", conversation_id).execute()
    if not conversation.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Verify user has permission for this conversation
    if conversation.data[0]["user_id"] != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add data to this conversation"
        )
    
    try:
        # Determine media type from content type
        content_type = file.content_type or "application/octet-stream"
        media_type = "image"
        if content_type.startswith("audio/"):
            media_type = "audio"
        elif content_type.startswith("video/"):
            media_type = "video"
        elif content_type.startswith("model/"):
            media_type = "3d_model"
        elif not content_type.startswith("image/"):
            media_type = "other"
        
        # Generate a unique filename
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        bucket_path = f"media/{conversation_id}/{unique_filename}"
        
        # Upload file to Supabase Storage
        contents = await file.read()
        storage_result = supabase.storage.from_("media").upload(
            bucket_path,
            contents
        )
        
        # Get public URL
        file_url = supabase.storage.from_("media").get_public_url(bucket_path)
        
        # Create multimodal data entry
        new_data = {
            "conversation_id": conversation_id,
            "type": media_type,
            "content_url": file_url,
            "metadata": {
                "filename": file.filename,
                "content_type": content_type,
                "size": len(contents)
            }
        }
        
        # Insert into database
        result = supabase.table("multimodal_data").insert(new_data).execute()
        
        return {
            "success": True,
            "file_url": file_url,
            "data": result.data[0] if result.data else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )

@router.get("/conversation/{conversation_id}", response_model=List[MultiModalDataResponse])
async def get_conversation_multimodal_data(
    conversation_id: str,
    current_user = Depends(get_current_active_user)
):
    """Get all multimodal data for a conversation"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if conversation exists and user has permission
    conversation = supabase.table("conversations").select("*").eq("id", conversation_id).execute()
    if not conversation.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    if conversation.data[0]["user_id"] != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation's data"
        )
    
    # Get all multimodal data for conversation
    multimodal_data = supabase.table("multimodal_data").select("*").eq("conversation_id", conversation_id).execute()
    return multimodal_data.data

@router.delete("/{data_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_multimodal_data(
    data_id: str,
    current_user = Depends(get_current_active_user)
):
    """Delete multimodal data"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if data exists
    data = supabase.table("multimodal_data").select("*").eq("id", data_id).execute()
    if not data.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Multimodal data not found"
        )
    
    # Check if conversation exists and user has permission
    conversation_id = data.data[0]["conversation_id"]
    conversation = supabase.table("conversations").select("*").eq("id", conversation_id).execute()
    
    if not conversation.data or (conversation.data[0]["user_id"] != current_user["id"] and current_user.get("role") != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this data"
        )
    
    # Delete from storage if URL is from our storage
    try:
        content_url = data.data[0]["content_url"]
        if "media" in content_url:
            # Extract path from URL
            path_parts = content_url.split("media/")
            if len(path_parts) > 1:
                path = f"media/{path_parts[1]}"
                supabase.storage.from_("media").remove(path)
    except:
        # Continue even if storage deletion fails
        pass
    
    # Delete from database
    supabase.table("multimodal_data").delete().eq("id", data_id).execute()
    
    return None
