from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from app.core.config import settings
from app.auth.jwt import create_access_token, verify_password, get_password_hash
from app.schemas.user import UserCreate, UserResponse, Token
from app.database.connection import get_supabase_client
import logging
import uuid

logger = logging.getLogger("app.api.auth")

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    logger.info(f"Attempting to register user: {user_data.email}")
    
    # Always try to re-initialize the connection
    client = get_supabase_client()
    logger.info(f"Refreshed supabase client: {client}")
    
    if not client:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Check if email already exists
    existing_user = client.table("users").select("*").eq("email", user_data.email).execute()
    if existing_user.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user_data.password)
    user_id = str(uuid.uuid4())
    current_time = datetime.utcnow()
    
    new_user = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": hashed_password,
        "subscription_level": "free",
        "created_at": current_time.isoformat(),
        "updated_at": current_time.isoformat()
    }
    
    # Insert user into database
    result = client.table("users").insert(new_user)
    
    # Construct a response regardless of the result data
    created_user = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "subscription_level": "free",
        "created_at": current_time
    }
    
    return created_user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login to get access token"""
    logger.info(f"Attempting login for user: {form_data.username}")
    
    # Always try to re-initialize the connection
    client = get_supabase_client()
    
    if not client:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    # Find user by email
    user_result = client.table("users").select("*").eq("email", form_data.username).execute()
    
    if not user_result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_result.data[0]
    
    # Verify password
    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "id": user["id"], "username": user["username"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
