from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.jwt import get_current_active_user
from app.schemas.conversation import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse
from app.database.connection import supabase
from app.services.conversation_service import (
    create_conversation as create_conversation_service,
    get_user_conversations as get_user_conversations_service,
    get_conversation as get_conversation_service,
    add_message as add_message_service,
    get_messages as get_messages_service,
    generate_character_response as generate_character_response_service
)
from typing import List, Dict, Any

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user = Depends(get_current_active_user)
):
    """Create a new conversation with a character"""
    return await create_conversation_service(
        user_id=current_user["id"],
        character_id=conversation_data.character_id,
        title=conversation_data.title
    )

@router.get("", response_model=List[ConversationResponse])
async def get_user_conversations(current_user = Depends(get_current_active_user)):
    """Get all conversations for current user"""
    return await get_user_conversations_service(user_id=current_user["id"])

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str, current_user = Depends(get_current_active_user)):
    """Get a specific conversation by ID"""
    return await get_conversation_service(
        conversation_id=conversation_id,
        user_id=current_user["id"]
    )

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user = Depends(get_current_active_user)
):
    """Add a new message to a conversation and get character response"""
    # Add the user's message
    user_message = await add_message_service(
        conversation_id=conversation_id,
        user_id=current_user["id"],
        content=message_data.content,
        is_user_message=True
    )
    
    # Generate character response
    character_message = await generate_character_response_service(
        conversation_id=conversation_id,
        user_id=current_user["id"],
        user_message=message_data.content
    )
    
    # Return the character's response message
    return character_message

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user = Depends(get_current_active_user)
):
    """Get all messages in a conversation"""
    return await get_messages_service(
        conversation_id=conversation_id,
        user_id=current_user["id"]
    )
