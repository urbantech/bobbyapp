"""
Character progression service for handling leveling, experience, and skill advancement.
"""

import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
import math
import json

from app.database.connection import supabase
from app.services.notification_service import create_character_notification
from app.schemas.notification import NotificationPriority
from app.utils.character_defaults import (
    get_level_xp_requirements,
    get_class_level_bonuses,
    get_xp_reward_values
)

logger = logging.getLogger(__name__)

# Load defaults from utility functions
LEVEL_XP_REQUIREMENTS = get_level_xp_requirements()
CLASS_LEVEL_BONUSES = get_class_level_bonuses()
XP_REWARD_VALUES = get_xp_reward_values()

async def add_experience(character_id: UUID, xp_amount: int) -> Dict[str, Any]:
    """
    Add experience points to a character and handle level ups.
    
    Args:
        character_id: The UUID of the character
        xp_amount: Amount of XP to add
        
    Returns:
        Dictionary with updated character info and level up data if applicable
    """
    try:
        # Get current character data
        character_result = supabase.table("characters").select("*").eq("id", str(character_id)).execute()
        
        if not character_result.data:
            logger.error(f"Character {character_id} not found")
            return {"success": False, "error": "Character not found"}
        
        character = character_result.data[0]
        current_level = character.get("level", 1)
        current_xp = character.get("experience", 0)
        character_class = character.get("character_class", "warrior").lower()
        stats = character.get("stats", {})
        abilities = character.get("abilities", {})
        
        # Calculate new XP total
        new_xp_total = current_xp + xp_amount
        
        # Check if character leveled up
        new_level = current_level
        level_ups = []
        
        # Check each level to see if we've gained multiple levels
        for level, xp_required in sorted(LEVEL_XP_REQUIREMENTS.items()):
            if level > current_level and new_xp_total >= xp_required:
                new_level = level
                level_data = await _process_level_up(character, level, character_class, stats, abilities)
                level_ups.append(level_data)
                
                # Update our working copies of stats and abilities
                stats = level_data.get("new_stats", stats)
                abilities = level_data.get("new_abilities", abilities)
        
        # Update character in database
        update_data = {
            "experience": new_xp_total,
            "updated_at": "now()"
        }
        
        # Only update level and stats if leveled up
        if new_level > current_level:
            update_data["level"] = new_level
            update_data["stats"] = stats
            update_data["abilities"] = abilities
        
        # Update the character
        result = supabase.table("characters").update(update_data).eq("id", str(character_id)).execute()
        
        if not result.data:
            logger.error(f"Failed to update XP for character {character_id}")
            return {"success": False, "error": "Failed to update character"}
        
        # Get the user_id for notifications
        user_id = character.get("created_by")
        
        # Send notifications for level ups if any
        if level_ups and user_id:
            for level_up in level_ups:
                level = level_up.get("level")
                await create_character_notification(
                    user_id=UUID(user_id),
                    character_id=character_id,
                    title=f"Level Up! {character['name']} is now level {level}",
                    message=_create_level_up_message(character['name'], level, level_up),
                    priority=NotificationPriority.HIGH
                )
        
        return {
            "success": True,
            "character": result.data[0],
            "xp_gained": xp_amount,
            "xp_total": new_xp_total,
            "previous_level": current_level,
            "new_level": new_level,
            "level_ups": level_ups if level_ups else None
        }
        
    except Exception as e:
        logger.error(f"Error adding experience points: {str(e)}")
        return {"success": False, "error": str(e)}


async def _process_level_up(character: Dict[str, Any], new_level: int, character_class: str, stats: Dict[str, Any], abilities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a character level up, updating stats and abilities.
    
    Args:
        character: Character data
        new_level: The new level
        character_class: Character's class
        stats: Current stats dictionary
        abilities: Current abilities dictionary
        
    Returns:
        Dictionary with level up information
    """
    # Initialize stats if needed
    if not stats:
        stats = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
            "health": 100,
            "mana": 100
        }
    
    # Initialize abilities if needed
    if not abilities:
        abilities = {
            "passive": [],
            "active": [],
            "special": []
        }
    
    # Get level bonuses for this character class and level
    level_bonuses = CLASS_LEVEL_BONUSES.get(character_class, {}).get(new_level, {})
    
    # Copy stats for modification
    new_stats = stats.copy()
    new_abilities = abilities.copy()
    
    # Apply stat bonuses
    stat_changes = {}
    if "stats" in level_bonuses:
        for stat, value in level_bonuses["stats"].items():
            if stat in new_stats:
                old_value = new_stats.get(stat, 0)
                new_stats[stat] = old_value + value
                stat_changes[stat] = {
                    "old": old_value,
                    "new": new_stats[stat],
                    "change": f"+{value}"
                }
    
    # Apply new abilities
    ability_changes = []
    if "abilities" in level_bonuses:
        for ability in level_bonuses["abilities"]:
            ability_type = _get_ability_type(ability, character_class)
            
            if ability_type and ability_type in new_abilities:
                if ability not in new_abilities[ability_type]:
                    new_abilities[ability_type].append(ability)
                    ability_changes.append({
                        "name": _format_ability_name(ability),
                        "description": _get_ability_description(ability, character_class),
                        "type": ability_type
                    })
    
    # Record the level up data
    level_up_data = {
        "level": new_level,
        "character_class": character_class,
        "stat_changes": stat_changes,
        "ability_changes": ability_changes,
        "new_stats": new_stats,
        "new_abilities": new_abilities,
        "xp_required": LEVEL_XP_REQUIREMENTS.get(new_level)
    }
    
    return level_up_data


def _create_level_up_message(character_name: str, level: int, level_up_data: Dict[str, Any]) -> str:
    """
    Create a notification message for a character level up.
    
    Args:
        character_name: The character's name
        level: The new level
        level_up_data: Level up information
        
    Returns:
        Formatted message
    """
    message = f"{character_name} has reached level {level}!\n\n"
    
    # Add stat changes
    if level_up_data.get("stat_changes"):
        message += "Stat improvements:\n"
        for stat, change in level_up_data["stat_changes"].items():
            message += f"• {stat.capitalize()}: {change['old']} → {change['new']} ({change['change']})\n"
        message += "\n"
    
    # Add ability changes
    if level_up_data.get("ability_changes"):
        message += "New abilities:\n"
        for ability in level_up_data["ability_changes"]:
            message += f"• {ability['name']} ({ability['type'].capitalize()}): {ability['description']}\n"
    
    return message


def _format_ability_name(ability_id: str) -> str:
    """
    Format an ability ID into a readable name.
    
    Args:
        ability_id: The ability ID (e.g., "fireball" or "power_strike")
        
    Returns:
        Formatted ability name
    """
    return " ".join(word.capitalize() for word in ability_id.replace("_", " ").split())


def _get_ability_description(ability_id: str, character_class: str) -> str:
    """
    Get a description for an ability.
    
    Args:
        ability_id: The ability ID
        character_class: The character's class
        
    Returns:
        Ability description
    """
    # In a full implementation, this would look up descriptions from a database
    # For now, we'll provide generic descriptions
    ability_name = _format_ability_name(ability_id)
    return f"A powerful {character_class} ability that allows you to use {ability_name}."


def _get_ability_type(ability_id: str, character_class: str) -> Optional[str]:
    """
    Determine the type of an ability (passive, active, special).
    
    Args:
        ability_id: The ability ID
        character_class: The character's class
        
    Returns:
        Ability type or None if not recognized
    """
    # This would ideally be determined by database lookup
    # For simplicity, we'll use a mapping approach
    ability_types = {
        # Warrior abilities
        "improved_combat_techniques": "passive",
        "battle_cry": "active",
        "second_wind": "active",
        "extra_attack": "passive",
        "defensive_stance": "active",
        "intimidating_presence": "passive",
        "improved_critical": "passive",
        "cleave": "active",
        "champion_s_might": "special",
        
        # Wizard abilities
        "arcane_recovery": "passive",
        "spell_school_specialization": "passive",
        "cantrip_mastery": "passive",
        "3rd_level_spells": "active",
        "arcane_tradition_feature": "passive",
        "4th_level_spells": "active",
        "5th_level_spells": "active",
        "arcane_mastery": "special",
        
        # Generic fallbacks for various ability types
        "improved": "passive",
        "mastery": "passive",
        "specialization": "passive",
        "recovery": "passive",
        "stance": "active",
        "strike": "active",
        "attack": "active",
        "cry": "active",
        "spells": "active",
        "shield": "active",
        "might": "special",
        "master": "special",
        "focus": "special",
        "rage": "special",
        "intervention": "special",
    }
    
    # Check for exact match
    if ability_id.lower().replace(" ", "_") in ability_types:
        return ability_types[ability_id.lower().replace(" ", "_")]
    
    # Check for partial match
    for key, value in ability_types.items():
        if key in ability_id.lower().replace(" ", "_"):
            return value
    
    # Default to active ability if no match
    return "active"


async def calculate_xp_reward(action_type: str, difficulty: str = "medium", success: bool = True) -> int:
    """
    Calculate XP reward for various actions.
    
    Args:
        action_type: Type of action (combat, quest, puzzle, exploration, roleplay, crafting)
        difficulty: Difficulty level
        success: Whether the action was successful
        
    Returns:
        XP amount to award
    """
    # Get base XP for the action type and difficulty
    action_rewards = XP_REWARD_VALUES.get(action_type.lower(), {})
    
    # Default XP values if the specific action type isn't found
    if not action_rewards:
        action_rewards = {
            "easy": 50,
            "medium": 100,
            "hard": 200,
            "minor": 50,
            "standard": 100,
            "major": 200,
            "epic": 500,
            "boss": 500,
            "location": 50,
            "secret": 100,
            "landmark": 150,
            "significant": 100,
            "basic": 50,
            "advanced": 100,
            "masterwork": 200
        }
    
    # Get base XP for the difficulty
    base_xp = action_rewards.get(difficulty.lower(), 100)
    
    # Apply success modifier
    if not success:
        # Partial XP for failed attempts
        base_xp = int(base_xp * 0.5)
    
    # Add some randomness (±10%)
    import random
    variation = random.uniform(0.9, 1.1)
    
    # Calculate final XP (rounded to nearest 5)
    final_xp = round(base_xp * variation / 5) * 5
    
    return max(5, final_xp)  # Ensure at least 5 XP is awarded
