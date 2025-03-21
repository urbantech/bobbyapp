"""
Database initialization script for Supabase.

This script creates all required tables in your Supabase project.
You would typically run this once when setting up the project.

Usage:
    python -m app.database.init_db
"""

import os
import sys
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to path to allow running as script
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """Get a Supabase client instance"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    
    return create_client(url, key)

def init_database():
    """Initialize database tables"""
    print("Initializing database...")
    
    # Get Supabase client
    try:
        supabase = get_supabase_client()
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Create users table
    print("Creating users table...")
    supabase.table("users").create({
        "id": "uuid",
        "username": "text",
        "email": "text",
        "password_hash": "text",
        "subscription_level": "text",
        "created_at": "timestamp with time zone",
        "updated_at": "timestamp with time zone"
    })
    
    # Create characters table
    print("Creating characters table...")
    supabase.table("characters").create({
        "id": "uuid",
        "name": "text",
        "character_class": "text",
        "backstory": "text",
        "personality": "jsonb",
        "stats": "jsonb",
        "inventory": "jsonb",
        "level": "integer",
        "health": "integer",
        "abilities": "jsonb",
        "created_by": "uuid references users(id)",
        "created_at": "timestamp with time zone",
        "updated_at": "timestamp with time zone"
    })
    
    # Create conversations table
    print("Creating conversations table...")
    supabase.table("conversations").create({
        "id": "uuid",
        "user_id": "uuid references users(id)",
        "character_id": "uuid references characters(id)",
        "messages": "jsonb",
        "created_at": "timestamp with time zone",
        "updated_at": "timestamp with time zone"
    })
    
    # Create dice_rolls table
    print("Creating dice_rolls table...")
    supabase.table("dice_rolls").create({
        "id": "uuid",
        "user_id": "uuid references users(id)",
        "character_id": "uuid references characters(id)",
        "dice_type": "integer",
        "result": "integer",
        "created_at": "timestamp with time zone"
    })
    
    # Create quests table
    print("Creating quests table...")
    supabase.table("quests").create({
        "id": "uuid",
        "name": "text",
        "description": "text",
        "difficulty": "text",
        "reward": "jsonb",
        "status": "text",
        "assigned_to": "uuid references users(id)",
        "created_at": "timestamp with time zone",
        "updated_at": "timestamp with time zone"
    })
    
    # Create multimodal_data table
    print("Creating multimodal_data table...")
    supabase.table("multimodal_data").create({
        "id": "uuid",
        "conversation_id": "uuid references conversations(id)",
        "type": "text",
        "content_url": "text",
        "created_at": "timestamp with time zone",
        "updated_at": "timestamp with time zone"
    })
    
    print("Database initialization complete!")

if __name__ == "__main__":
    init_database()
