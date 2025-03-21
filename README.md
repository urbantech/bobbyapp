# BobbyApp - AI RPG & Roleplaying Platform

An immersive platform for creating and interacting with AI-powered roleplaying characters, complete with RPG mechanics.

## Features

- **AI Character System**: Create and customize AI characters with unique personalities
- **Contextual Memory**: AI characters remember past interactions for immersive conversations
- **RPG Mechanics**: Character stats, dice rolls, quests, and inventory management
- **Multimodal Support**: AI-generated avatars, voice interactions, and animated expressions
- **Multiplayer Features**: Collaborative roleplaying with AI and other players
- **Admin Dashboard**: Comprehensive tools for game masters and administrators
- **Robust Error Handling**: Consistent error responses and logging system

## Technology Stack

- **Backend**: Python (FastAPI), Supabase (PostgreSQL)
- **AI Components**: Ollama (Local LLMs), LangChain, Pinecone (Vector Storage)
- **Multimodal AI**: Stable Diffusion (images), Whisper (STT), Coqui TTS (voice)
- **Database Migrations**: SQL scripts and versioning for schema changes

## Getting Started

### Prerequisites

- Python 3.9+
- Supabase account (or local PostgreSQL)
- Optional: CUDA-capable GPU for AI processing

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourname/bobbyapp.git
   cd bobbyapp
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Setup environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

5. Initialize the database:
   ```bash
   python -m app.database.init_db
   ```

### Running the Application

Start the FastAPI server:
```bash
python -m app.main
```

The API will be available at `http://localhost:8000` and the Swagger documentation at `http://localhost:8000/docs`.

## API Endpoints

The API follows a RESTful structure with these main resources:

- **Authentication**: `/api/v1/auth/` - Register, login, and token management
- **Users**: `/api/v1/users/` - User profile management
- **Characters**: `/api/v1/characters/` - AI character creation and interaction
- **Conversations**: `/api/v1/conversations/` - Dialogues with AI characters
- **Dice Rolls**: `/api/v1/dice/` - RPG mechanics for randomized outcomes
- **Quests**: `/api/v1/quests/` - Adventure management and progression
- **Multimodal**: `/api/v1/multimodal/` - Image, audio, and video content management
- **Admin**: `/api/v1/admin/` - Admin-only endpoints for system management

## Project Structure

```
bobbyapp/
├── app/
│   ├── api/          # API routes
│   ├── auth/         # Authentication utilities
│   ├── core/         # Core configuration
│   ├── database/     # Database connection and utilities
│   │   └── migrations/  # SQL migration scripts
│   ├── middleware/   # Custom middleware (error handlers, etc.)
│   ├── models/       # Data models
│   ├── schemas/      # Pydantic schemas for API
│   ├── services/     # Business logic services
│   ├── tests/        # Unit and integration tests
│   ├── utils/        # Utility functions
│   └── main.py       # Application entry point
├── docs/             # Documentation
├── .env.example      # Example environment variables
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Database Migrations

The `app/database/migrations/` directory contains SQL scripts for database schema changes. 

To apply migrations to your Supabase database:
1. Connect to your Supabase instance
2. Use the SQL Editor tool in the Supabase dashboard
3. Run the migration scripts in the correct order (they are numbered)

For local development with PostgreSQL, you can run:
```bash
psql -U your_username -d your_database -a -f app/database/migrations/initial_schema.sql
```

## Error Handling

BobbyApp implements a comprehensive error handling system that:
- Provides consistent error responses across all API endpoints
- Includes detailed validation error messages for easier debugging
- Logs errors with appropriate severity levels
- Prevents exposure of sensitive information in production

## Admin Features

The admin API provides tools for game masters and system administrators:
- System statistics and health monitoring
- User management and role assignments
- Character moderation and management
- Quest and conversation oversight

Admin endpoints are protected and require admin privileges to access.

## Development Roadmap

This project follows the sprint plan outlined in `sprintplan.md`, with six two-week sprints:

1. **Foundation Setup**: Backend and database infrastructure (current)
2. **AI Conversations**: LLM integration and basic interactions
3. **RPG Mechanics**: Stats, dice rolls, quests
4. **Multimodal Support**: Voice, avatars, animations
5. **AI Personalization**: Fine-tuning and learning
6. **Multiplayer & Final Enhancements**: Collaborative features

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
