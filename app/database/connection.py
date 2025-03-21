"""
Database connection management for the application.
"""

import os
import logging
import json
import requests
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.database")

# Global variables
supabase = None
SUPABASE_URL = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU")

class DummyResult:
    def __init__(self, data, error):
        self.data = data
        self.error = error

# Direct REST API client for Supabase
class SupabaseClient:
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
    
    def table(self, table_name: str):
        return TableQuery(self, table_name)

class TableQuery:
    def __init__(self, client: SupabaseClient, table_name: str):
        self.client = client
        self.table_name = table_name
        self.query_params = {}
        self.filters = []
    
    def select(self, columns: str = "*"):
        self.query_params["select"] = columns
        return self
    
    def eq(self, column: str, value: Any):
        self.filters.append(f"{column}=eq.{value}")
        return self
    
    def limit(self, limit: int):
        self.query_params["limit"] = limit
        return self
    
    def insert(self, data: Dict[str, Any] or List[Dict[str, Any]]):
        url = f"{self.client.url}/rest/v1/{self.table_name}"
        
        if not isinstance(data, list):
            data = [data]
            
        response = requests.post(
            url,
            headers=self.client.headers,
            json=data
        )
        
        if response.status_code >= 400:
            logger.error(f"Insert error: {response.status_code} - {response.text}")
            return DummyResult([], f"Error: {response.status_code} - {response.text}")
        
        try:
            # Try to parse JSON but handle empty responses
            result = response.json() if response.text else []
            return DummyResult(result, None)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)} - Response: {response.text}")
            return DummyResult([], f"JSON decode error: {str(e)}")
    
    def update(self, data: Dict[str, Any]):
        filter_query = "&".join(self.filters)
        url = f"{self.client.url}/rest/v1/{self.table_name}?{filter_query}"
        
        response = requests.patch(
            url,
            headers=self.client.headers,
            json=data
        )
        
        if response.status_code >= 400:
            logger.error(f"Update error: {response.status_code} - {response.text}")
            return DummyResult([], f"Error: {response.status_code} - {response.text}")
        
        try:
            # Try to parse JSON but handle empty responses
            result = response.json() if response.text else []
            return DummyResult(result, None)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)} - Response: {response.text}")
            return DummyResult([], f"JSON decode error: {str(e)}")
    
    def execute(self):
        filter_query = "&".join(self.filters)
        select_query = self.query_params.get("select", "*")
        limit_query = f"limit={self.query_params.get('limit', 100)}" if "limit" in self.query_params else ""
        
        query_parts = [p for p in [filter_query, limit_query] if p]
        query_string = "&".join(query_parts)
        
        url = f"{self.client.url}/rest/v1/{self.table_name}?select={select_query}"
        if query_string:
            url += f"&{query_string}"
        
        logger.debug(f"Executing query: {url}")
        response = requests.get(
            url,
            headers=self.client.headers
        )
        
        if response.status_code >= 400:
            logger.error(f"Query error: {response.status_code} - {response.text}")
            return DummyResult([], f"Error: {response.status_code} - {response.text}")
        
        try:
            # Try to parse JSON but handle empty responses
            result = response.json() if response.text else []
            return DummyResult(result, None)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)} - Response: {response.text}")
            return DummyResult([], f"JSON decode error: {str(e)}")

def get_supabase_client():
    """
    Get or initialize our custom Supabase client.
    
    Returns:
        Supabase client instance
    """
    global supabase
    
    if supabase is not None:
        return supabase
    
    try:
        # Initialize our custom Supabase client
        logger.info(f"Connecting to Supabase at {SUPABASE_URL}")
        supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
        
        # Test the connection with a simple query
        test_result = supabase.table("users").select("*").limit(1).execute()
        logger.info(f"Supabase connection test successful")
        
        return supabase
    except Exception as e:
        logger.error(f"Error initializing Supabase client: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
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
        # Try executing a simple query
        result = client.table("users").select("*").limit(1).execute()
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False

def close_connection():
    """
    Close the database connection.
    """
    global supabase
    supabase = None
    logger.info("Database connection closed")
