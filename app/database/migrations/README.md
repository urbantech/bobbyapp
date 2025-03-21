# Database Migrations

This directory contains database migration scripts using Alembic for the BobbyApp RPG platform.

## Migration Workflow

1. **Create a new migration**:
   ```bash
   alembic revision -m "description_of_change"
   ```

2. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

3. **Rollback migrations**:
   ```bash
   alembic downgrade -1
   ```

## Migration Best Practices

- Each migration should be atomic and focused on a single change
- Always provide both upgrade and downgrade scripts
- Test migrations in a development environment before applying to production
- Back up your database before running migrations in production

## Database Structure

The current database structure includes the following tables:

- **users**: User authentication and profile data
- **characters**: RPG character information
- **conversations**: Conversations between users and characters
- **messages**: Individual messages within conversations
- **quests**: Quest information and tracking
- **dice_rolls**: Records of dice rolls
- **multimodal_data**: Images, audio, and other media associated with conversations

## Supabase Setup

When using Supabase, you can apply these migrations using the SQL editor in the Supabase dashboard or by connecting directly to the PostgreSQL database.
