from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from dotenv import load_dotenv

# Import routers
from app.api import auth, users, characters, conversations, dice, quests, multimodal, admin, notifications, inventory, character_progression, items

# Import middleware and utils
from app.middleware.error_handlers import register_exception_handlers
from app.database.connection import get_supabase_client, check_database_connection

# Configure logging
logger = logging.getLogger("app.main")
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

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
    logger.info("Initializing database connection")
    client = get_supabase_client()
    if client:
        logger.info("Database connection successfully initialized")
        connection_ok = check_database_connection()
        logger.info(f"Database connection check: {'OK' if connection_ok else 'FAILED'}")
    else:
        logger.error("Failed to initialize database connection")

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
app.include_router(items.router, prefix=api_prefix)

@app.get("/")
async def root():
    return {"message": "Welcome to BobbyApp API", "status": "online"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
