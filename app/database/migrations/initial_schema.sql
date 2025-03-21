-- Initial database schema for BobbyApp RPG Platform
-- This script creates all necessary tables for the application

-- Enable UUID extension for generating unique IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create types and enums
CREATE TYPE notification_type AS ENUM ('system', 'quest', 'character', 'achievement', 'combat', 'message');
CREATE TYPE notification_priority AS ENUM ('low', 'medium', 'high');
CREATE TYPE item_rarity AS ENUM ('common', 'uncommon', 'rare', 'epic', 'legendary', 'artifact');
CREATE TYPE item_type AS ENUM ('weapon', 'armor', 'potion', 'scroll', 'quest', 'material', 'food', 'container', 'misc');
CREATE TYPE equipment_slot AS ENUM ('head', 'neck', 'chest', 'back', 'hands', 'waist', 'legs', 'feet', 'main_hand', 'off_hand', 'finger_1', 'finger_2', 'trinket_1', 'trinket_2');
CREATE TYPE character_class AS ENUM ('warrior', 'mage', 'rogue', 'cleric', 'ranger');

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Characters table
CREATE TABLE IF NOT EXISTS characters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    character_class character_class NOT NULL,
    backstory TEXT,
    personality JSONB,
    stats JSONB NOT NULL DEFAULT '{}'::JSONB,
    inventory JSONB NOT NULL DEFAULT '[]'::JSONB,
    level INTEGER NOT NULL DEFAULT 1,
    experience INTEGER NOT NULL DEFAULT 0,
    health INTEGER NOT NULL DEFAULT 100,
    abilities JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quests table
CREATE TABLE IF NOT EXISTS quests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    objectives JSONB NOT NULL,
    rewards JSONB,
    requirements JSONB,
    difficulty TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Character_quests table (many-to-many)
CREATE TABLE IF NOT EXISTS character_quests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    quest_id UUID NOT NULL REFERENCES quests(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'in_progress',
    progress JSONB NOT NULL DEFAULT '{}'::JSONB,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(character_id, quest_id)
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT,
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    summary TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    sender_type TEXT NOT NULL, -- 'user', 'character', 'system'
    sender_id TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Dice_rolls table
CREATE TABLE IF NOT EXISTS dice_rolls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    dice_type TEXT NOT NULL,
    dice_count INTEGER NOT NULL,
    modifier INTEGER DEFAULT 0,
    results JSONB NOT NULL,
    total INTEGER NOT NULL,
    context TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    character_id UUID REFERENCES characters(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    notification_type notification_type NOT NULL DEFAULT 'system',
    priority notification_priority NOT NULL DEFAULT 'medium',
    read BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Items table
CREATE TABLE IF NOT EXISTS items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    item_type item_type NOT NULL,
    rarity item_rarity NOT NULL DEFAULT 'common',
    value INTEGER NOT NULL DEFAULT 0,
    weight FLOAT NOT NULL DEFAULT 0,
    stackable BOOLEAN NOT NULL DEFAULT FALSE,
    max_stack INTEGER NOT NULL DEFAULT 1,
    effects JSONB,
    requirements JSONB,
    equipment_slot equipment_slot,
    stats JSONB,
    metadata JSONB,
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inventory table (character's inventory items)
CREATE TABLE IF NOT EXISTS inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    equipped BOOLEAN NOT NULL DEFAULT FALSE,
    durability INTEGER,
    custom_name TEXT,
    custom_description TEXT,
    custom_effects JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crafting_recipes table
CREATE TABLE IF NOT EXISTS crafting_recipes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    skill_required TEXT,
    skill_level INTEGER,
    materials JSONB NOT NULL,
    result_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    result_quantity INTEGER NOT NULL DEFAULT 1,
    crafting_time INTEGER NOT NULL, -- in seconds
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_characters_created_by ON characters(created_by);
CREATE INDEX IF NOT EXISTS idx_quests_created_by ON quests(created_by);
CREATE INDEX IF NOT EXISTS idx_character_quests_character_id ON character_quests(character_id);
CREATE INDEX IF NOT EXISTS idx_character_quests_quest_id ON character_quests(quest_id);
CREATE INDEX IF NOT EXISTS idx_conversations_character_id ON conversations(character_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_dice_rolls_user_id ON dice_rolls(user_id);
CREATE INDEX IF NOT EXISTS idx_dice_rolls_character_id ON dice_rolls(character_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read);
CREATE INDEX IF NOT EXISTS idx_inventory_character_id ON inventory(character_id);
CREATE INDEX IF NOT EXISTS idx_inventory_item_id ON inventory(item_id);
CREATE INDEX IF NOT EXISTS idx_inventory_equipped ON inventory(equipped);
CREATE INDEX IF NOT EXISTS idx_items_item_type ON items(item_type);
CREATE INDEX IF NOT EXISTS idx_items_rarity ON items(rarity);
CREATE INDEX IF NOT EXISTS idx_items_equipment_slot ON items(equipment_slot);

-- Create or replace functions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at columns
CREATE TRIGGER set_updated_at_users
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_characters
BEFORE UPDATE ON characters
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_quests
BEFORE UPDATE ON quests
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_conversations
BEFORE UPDATE ON conversations
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_notifications
BEFORE UPDATE ON notifications
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_items
BEFORE UPDATE ON items
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_updated_at_inventory
BEFORE UPDATE ON inventory
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create RLS (Row-Level Security) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE characters ENABLE ROW LEVEL SECURITY;
ALTER TABLE quests ENABLE ROW LEVEL SECURITY;
ALTER TABLE character_quests ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE dice_rolls ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE crafting_recipes ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY users_policy ON users
    USING (id = auth.uid() OR role = 'admin');

-- Characters policy
CREATE POLICY characters_policy ON characters
    USING (created_by = auth.uid() OR 
          (SELECT role FROM users WHERE id = auth.uid()) = 'admin');

-- Quests policy
CREATE POLICY quests_policy ON quests
    USING (created_by = auth.uid() OR 
          (SELECT role FROM users WHERE id = auth.uid()) = 'admin');

-- Character_quests policy
CREATE POLICY character_quests_policy ON character_quests
    USING (character_id IN (SELECT id FROM characters WHERE created_by = auth.uid()) OR 
          (SELECT role FROM users WHERE id = auth.uid()) = 'admin');

-- Conversations policy
CREATE POLICY conversations_policy ON conversations
    USING (user_id = auth.uid() OR 
          (SELECT role FROM users WHERE id = auth.uid()) = 'admin');

-- Messages policy
CREATE POLICY messages_policy ON messages
    USING (conversation_id IN (SELECT id FROM conversations WHERE user_id = auth.uid()) OR 
          (SELECT role FROM users WHERE id = auth.uid()) = 'admin');

-- Dice_rolls policy
CREATE POLICY dice_rolls_policy ON dice_rolls
    USING (user_id = auth.uid() OR 
          (SELECT role FROM users WHERE id = auth.uid()) = 'admin');

-- Notifications policy
CREATE POLICY notifications_policy ON notifications
    USING (user_id = auth.uid() OR 
          (SELECT role FROM users WHERE id = auth.uid()) = 'admin');

-- Items policy (everyone can view items)
CREATE POLICY items_policy ON items
    USING (TRUE);

-- Inventory policy
CREATE POLICY inventory_policy ON inventory
    USING (character_id IN (SELECT id FROM characters WHERE created_by = auth.uid()) OR 
          (SELECT role FROM users WHERE id = auth.uid()) = 'admin');

-- Crafting recipes policy (everyone can view recipes)
CREATE POLICY crafting_recipes_policy ON crafting_recipes
    USING (TRUE);
