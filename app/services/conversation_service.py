"""
Service layer for handling conversation operations.
This separates the business logic from the API endpoints.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from app.database.connection import supabase
from app.utils.ai_responses import get_character_response
from fastapi import HTTPException, status

async def create_conversation(
    user_id: str,
    character_id: str,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new conversation between a user and a character.
    
    Args:
        user_id: The ID of the user
        character_id: The ID of the character
        title: Optional title for the conversation
        
    Returns:
        The created conversation data
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if character exists
    character = supabase.table("characters").select("*").eq("id", character_id).execute()
    if not character.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # Generate default title if not provided
    if not title:
        char_name = character.data[0]["name"]
        title = f"Conversation with {char_name} - {datetime.utcnow().strftime('%Y-%m-%d')}"
    
    # Create conversation
    new_conversation = {
        "user_id": user_id,
        "character_id": character_id,
        "title": title,
        "status": "active"
    }
    
    result = supabase.table("conversations").insert(new_conversation).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )
    
    return result.data[0]

async def get_user_conversations(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all conversations for a user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        List of conversation data
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    result = supabase.table("conversations").select("*").eq("user_id", user_id).execute()
    return result.data

async def get_conversation(conversation_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get a specific conversation.
    
    Args:
        conversation_id: The ID of the conversation
        user_id: The ID of the user (for permission check)
        
    Returns:
        Conversation data
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Get conversation
    conversation = supabase.table("conversations").select("*").eq("id", conversation_id).execute()
    if not conversation.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check permission
    if conversation.data[0]["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )
    
    return conversation.data[0]

async def add_message(
    conversation_id: str,
    user_id: str,
    content: str,
    is_user_message: bool = True
) -> Dict[str, Any]:
    """
    Add a message to a conversation.
    
    Args:
        conversation_id: The ID of the conversation
        user_id: The ID of the user (for permission check)
        content: The message content
        is_user_message: Whether the message is from the user (True) or character (False)
        
    Returns:
        The created message data
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if conversation exists and user has permission
    conversation = await get_conversation(conversation_id, user_id)
    
    # Create message
    new_message = {
        "conversation_id": conversation_id,
        "content": content,
        "is_user_message": is_user_message
    }
    
    result = supabase.table("messages").insert(new_message).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add message"
        )
    
    return result.data[0]

async def get_messages(conversation_id: str, user_id: str) -> List[Dict[str, Any]]:
    """
    Get all messages for a conversation.
    
    Args:
        conversation_id: The ID of the conversation
        user_id: The ID of the user (for permission check)
        
    Returns:
        List of message data
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if conversation exists and user has permission
    await get_conversation(conversation_id, user_id)
    
    # Get messages
    messages = supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).execute()
    return messages.data

async def generate_character_response(
    conversation_id: str,
    user_id: str,
    user_message: str
) -> Dict[str, Any]:
    """
    Generate an AI response from a character based on a user message.
    
    Args:
        conversation_id: The ID of the conversation
        user_id: The ID of the user (for permission check)
        user_message: The user's message
        
    Returns:
        The character's response message data
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if conversation exists and user has permission
    conversation = await get_conversation(conversation_id, user_id)
    
    # Get character
    character_id = conversation["character_id"]
    character = supabase.table("characters").select("*").eq("id", character_id).execute()
    if not character.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # Get conversation history
    messages = await get_messages(conversation_id, user_id)
    
    # Add user message to conversation
    await add_message(conversation_id, user_id, user_message, is_user_message=True)
    
    # Generate AI response
    character_data = character.data[0]
    response_content = get_character_response(
        character=character_data,
        user_message=user_message,
        conversation_history=messages
    )
    
    # Add character message to conversation
    character_message = await add_message(
        conversation_id, 
        user_id, 
        response_content, 
        is_user_message=False
    )
    
    return character_message
