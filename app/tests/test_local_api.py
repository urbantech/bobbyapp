"""
Test script for API endpoints with local Supabase
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

# Token storage
access_token = None

def print_separator():
    print("\n" + "="*80 + "\n")

def test_register():
    """Test user registration"""
    print("Testing User Registration...")
    
    # Generate a unique username and email
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    user_data = {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "password123"
    }
    
    response = requests.post(
        f"{API_BASE_URL}{API_PREFIX}/auth/register",
        json=user_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 201, "User registration failed"
    return user_data

def test_login(user_data):
    """Test user login"""
    global access_token
    
    print_separator()
    print("Testing User Login...")
    
    login_data = {
        "username": user_data["email"],  # OAuth2 form expects username
        "password": user_data["password"]
    }
    
    response = requests.post(
        f"{API_BASE_URL}{API_PREFIX}/auth/token",
        data=login_data  # Use data instead of json for form data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200, "Login failed"
    
    # Store the token for later use
    access_token = response.json()["access_token"]
    return access_token

def test_create_character():
    """Test character creation"""
    global access_token
    
    print_separator()
    print("Testing Character Creation...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    character_data = {
        "name": "Gandalf",
        "character_class": "Wizard",
        "attributes": {
            "strength": 10,
            "intelligence": 18,
            "dexterity": 12,
            "charisma": 14,
            "wisdom": 16,
            "constitution": 11
        },
        "appearance": {
            "hair": "gray",
            "eyes": "blue",
            "height": "6.0",
            "features": "Long beard and pointy hat"
        },
        "backstory": "A wandering wizard with great power and wisdom."
    }
    
    response = requests.post(
        f"{API_BASE_URL}{API_PREFIX}/characters",
        json=character_data,
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code in [201, 200], "Character creation failed"
    return response.json()["id"]

def test_get_character(character_id):
    """Test retrieving a character"""
    global access_token
    
    print_separator()
    print(f"Testing Get Character (ID: {character_id})...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(
        f"{API_BASE_URL}{API_PREFIX}/characters/{character_id}",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200, "Failed to retrieve character"

def test_list_characters():
    """Test listing all characters for a user"""
    global access_token
    
    print_separator()
    print("Testing List Characters...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(
        f"{API_BASE_URL}{API_PREFIX}/characters",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200, "Failed to list characters"

def test_get_items():
    """Test retrieving items"""
    global access_token
    
    print_separator()
    print("Testing Get Items...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(
        f"{API_BASE_URL}{API_PREFIX}/items",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200, "Failed to retrieve items"

def run_tests():
    """Run all tests in sequence"""
    try:
        # Register a new user
        user_data = test_register()
        
        # Login with the new user
        test_login(user_data)
        
        # Create a character
        character_id = test_create_character()
        
        # Get the character details
        test_get_character(character_id)
        
        # List all characters
        test_list_characters()
        
        # Get items
        test_get_items()
        
        print_separator()
        print("All tests completed successfully!")
        
    except AssertionError as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
