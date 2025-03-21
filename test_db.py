"""
Test script for direct Supabase connection
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase Config
SUPABASE_URL = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU")

def test_direct_connection():
    print(f"Testing direct connection to Supabase at {SUPABASE_URL}")
    
    # Attempt to query users directly with REST API
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        users_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/users?select=*&limit=5",
            headers=headers
        )
        
        print(f"Users query status code: {users_response.status_code}")
        if users_response.status_code == 200:
            print(f"Users data: {users_response.json()}")
        else:
            print(f"Error response: {users_response.text}")
        
    except Exception as e:
        print(f"Error querying users: {str(e)}")
        
    # Try to create a test user
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    test_user = {
        "username": f"direct_test_{unique_id}",
        "email": f"direct_{unique_id}@example.com",
        "password_hash": "test_hash_123",
        "subscription_level": "free"
    }
    
    try:
        create_response = requests.post(
            f"{SUPABASE_URL}/rest/v1/users",
            headers=headers,
            json=[test_user]  # Supabase expects a list
        )
        
        print(f"User creation status code: {create_response.status_code}")
        if create_response.status_code < 300:
            print(f"Created user data: {create_response.json() if create_response.text else 'No response data'}")
        else:
            print(f"Error response: {create_response.text}")
            
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        
if __name__ == "__main__":
    test_direct_connection()
