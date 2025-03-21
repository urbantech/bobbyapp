from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Import routers
from app.api import auth, users, characters, conversations, dice, quests, multimodal, admin, notifications, inventory, character_progression

# Import middleware and utils
from app.middleware.error_handlers import register_exception_handlers
from app.database.connection import get_supabase_client

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="BobbyApp - AI RPG & Roleplaying Platform",
    description="An immersive platform for AI-powered roleplaying characters",
    version="0.1.0"
)

# Register exception handlers
register_exception_handlers(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database connection
@app.on_event("startup")
async def startup_db_client():
    get_supabase_client()

# Include routers
api_prefix = os.getenv("API_PREFIX", "/api/v1")
app.include_router(auth.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
app.include_router(characters.router, prefix=api_prefix)
app.include_router(conversations.router, prefix=api_prefix)
app.include_router(dice.router, prefix=api_prefix)
app.include_router(quests.router, prefix=api_prefix)
app.include_router(multimodal.router, prefix=api_prefix)
app.include_router(admin.router, prefix=api_prefix)
app.include_router(notifications.router, prefix=api_prefix)
app.include_router(inventory.router, prefix=api_prefix)
app.include_router(character_progression.router, prefix=api_prefix)

@app.get("/")
async def root():
    return {"message": "Welcome to BobbyApp API", "status": "online"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
