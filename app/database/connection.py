"""
Database connection management for the application.
"""

import os
from supabase import create_client, Client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.database")

# Initialize Supabase client
supabase: Client = None

def get_supabase_client() -> Client:
    """
    Get or initialize the Supabase client.
    
    Returns:
        Supabase client instance
    """
    global supabase
    
    if supabase is not None:
        return supabase
    
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.warning("Supabase credentials not found in environment variables")
        return None
    
    try:
        # Initialize Supabase client
        supabase = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
        return supabase
    except Exception as e:
        logger.error(f"Error initializing Supabase client: {str(e)}")
        return None

def check_database_connection() -> bool:
    """
    Check if the database connection is working.
    
    Returns:
        True if connection is successful, False otherwise
    """
    client = get_supabase_client()
    
    if not client:
        return False
    
    try:
        # Simple query to test connection
        result = client.table("users").select("count(*)", count="exact").execute()
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

def close_connection():
    """Close the Supabase client connection if open."""
    global supabase
    if supabase:
        # Supabase Python client doesn't have an explicit close method
        # Just set to None to help with garbage collection
        supabase = None
        logger.info("Supabase client connection released")
