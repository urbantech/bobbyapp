# Unity Integration Guide for BobbyApp API

## Local Development Setup

### 1. Environment Setup

Create a `.env` file in the root directory with the following configuration:
```
# API Configuration
API_PREFIX=/api/v1

# Security
SECRET_KEY=development_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database - Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres

# AI Services (using mock responses for development)
AI_PROVIDER=mock

# Media Storage
MEDIA_BUCKET=media
MAX_UPLOAD_SIZE=10485760  # 10 MB in bytes

# Logging
LOG_LEVEL=INFO

# Development mode
DEBUG=True
```

Replace `your_supabase_url` and `your_supabase_key` with your actual Supabase credentials.

### 2. Install Dependencies

```
pip install -r requirements.txt
```

### 3. Run the FastAPI Server

```
python run.py
```

The server will run on `http://localhost:8000` with hot reloading enabled.

## Unity Integration

### 1. REST API Communication

In your Unity project, use the UnityWebRequest class to communicate with the FastAPI backend:

```csharp
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using System.Text;
using System.Threading.Tasks;

public class ApiClient : MonoBehaviour
{
    private string _baseUrl = "http://localhost:8000/api/v1";
    private string _authToken;

    // Login and get authentication token
    public async Task<bool> Login(string email, string password)
    {
        string url = $"{_baseUrl}/auth/login";
        string jsonPayload = JsonUtility.ToJson(new LoginRequest { email = email, password = password });
        
        using (UnityWebRequest request = UnityWebRequest.Post(url, jsonPayload))
        {
            request.SetRequestHeader("Content-Type", "application/json");
            
            await request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                LoginResponse response = JsonUtility.FromJson<LoginResponse>(request.downloadHandler.text);
                _authToken = response.access_token;
                return true;
            }
            else
            {
                Debug.LogError($"Login Error: {request.error}");
                return false;
            }
        }
    }
    
    // Example: Get Character Data
    public async Task<CharacterData> GetCharacter(string characterId)
    {
        string url = $"{_baseUrl}/characters/{characterId}";
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.SetRequestHeader("Authorization", $"Bearer {_authToken}");
            
            await request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                return JsonUtility.FromJson<CharacterData>(request.downloadHandler.text);
            }
            else
            {
                Debug.LogError($"Get Character Error: {request.error}");
                return null;
            }
        }
    }
    
    // Example: Add Character Experience
    public async Task<bool> AddExperience(string characterId, int xpAmount)
    {
        string url = $"{_baseUrl}/character-progression/{characterId}/experience";
        string jsonPayload = JsonUtility.ToJson(new XpRequest { xp_amount = xpAmount });
        
        using (UnityWebRequest request = UnityWebRequest.Post(url, jsonPayload))
        {
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Authorization", $"Bearer {_authToken}");
            
            await request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                return true;
            }
            else
            {
                Debug.LogError($"Add Experience Error: {request.error}");
                return false;
            }
        }
    }
}

// Request and response classes
[System.Serializable]
public class LoginRequest
{
    public string email;
    public string password;
}

[System.Serializable]
public class LoginResponse
{
    public string access_token;
    public string token_type;
}

[System.Serializable]
public class XpRequest
{
    public int xp_amount;
}

[System.Serializable]
public class CharacterData
{
    public string id;
    public string name;
    public string character_class;
    public int level;
    public int experience;
    // Add other fields as needed
}
```

### 2. API Documentation

Access the interactive API documentation at `http://localhost:8000/docs` to see all available endpoints and their expected request/response formats.

### 3. Development Workflow

1. Run the FastAPI server locally
2. Set up your Unity project to connect to `http://localhost:8000/api/v1`
3. Implement Unity C# scripts to interact with the API endpoints
4. Test the integration with mock data first

### 4. Production Deployment

For production deployment, update the base URL in your Unity client to point to your production API server.
