"""
Utility functions for generating default character attributes based on class.
Provides default stats, abilities, and other attributes for new characters.
"""

from typing import Dict, Any, List


def get_default_stats(character_class: str) -> Dict[str, int]:
    """
    Get default character stats based on character class.
    
    Args:
        character_class: The character's class (e.g., warrior, wizard)
        
    Returns:
        Dictionary of stat values
    """
    # Base stats for all characters
    base_stats = {
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10
    }
    
    # Class-specific stat adjustments
    class_modifiers = {
        "warrior": {"strength": 5, "constitution": 3, "dexterity": 2},
        "wizard": {"intelligence": 5, "wisdom": 3, "constitution": -1},
        "rogue": {"dexterity": 5, "charisma": 2, "intelligence": 2},
        "cleric": {"wisdom": 5, "charisma": 2, "constitution": 2},
        "bard": {"charisma": 5, "dexterity": 2, "intelligence": 2},
        "ranger": {"dexterity": 4, "wisdom": 3, "strength": 2},
        "paladin": {"strength": 3, "charisma": 3, "constitution": 3},
        "druid": {"wisdom": 4, "constitution": 3, "intelligence": 2},
        "monk": {"dexterity": 4, "wisdom": 3, "strength": 2},
        "sorcerer": {"charisma": 5, "constitution": 2, "intelligence": 2},
    }
    
    # Apply class modifiers to base stats
    char_class = character_class.lower()
    if char_class in class_modifiers:
        for stat, modifier in class_modifiers[char_class].items():
            base_stats[stat] += modifier
    
    return base_stats


def get_default_abilities(character_class: str) -> Dict[str, Any]:
    """
    Get default abilities based on character class.
    
    Args:
        character_class: The character's class
        
    Returns:
        Dictionary of abilities
    """
    # Basic abilities shared by all classes
    basic_abilities = {
        "passive": ["Rest", "Observe"],
        "active": ["Attack"],
        "special": []
    }
    
    # Class-specific abilities
    class_abilities = {
        "warrior": {
            "passive": ["Toughness", "Intimidate"],
            "active": ["Power Strike", "Shield Block", "Charge"],
            "special": ["Berserker Rage"]
        },
        "wizard": {
            "passive": ["Arcane Knowledge", "Spell Focus"],
            "active": ["Fireball", "Magic Missile", "Arcane Shield"],
            "special": ["Teleport", "Time Manipulation"]
        },
        "rogue": {
            "passive": ["Stealth", "Trap Detection"],
            "active": ["Backstab", "Pickpocket", "Evasion"],
            "special": ["Shadow Strike"]
        },
        "cleric": {
            "passive": ["Divine Favor", "Healing Aura"],
            "active": ["Heal", "Smite", "Bless"],
            "special": ["Divine Intervention"]
        },
        "bard": {
            "passive": ["Charismatic Aura", "Lore Knowledge"],
            "active": ["Inspire", "Soothing Song", "Distraction"],
            "special": ["Epic Performance"]
        },
        "ranger": {
            "passive": ["Track", "Animal Empathy"],
            "active": ["Precise Shot", "Animal Companion", "Nature's Eye"],
            "special": ["One With Nature"]
        },
        "paladin": {
            "passive": ["Divine Sense", "Aura of Protection"],
            "active": ["Lay on Hands", "Divine Smite", "Sacred Oath"],
            "special": ["Holy Avenger"]
        },
        "druid": {
            "passive": ["Nature Bond", "Wild Empathy"],
            "active": ["Wild Shape", "Entangle", "Speak with Animals"],
            "special": ["Nature's Wrath"]
        },
        "monk": {
            "passive": ["Meditation", "Unarmored Defense"],
            "active": ["Flurry of Blows", "Stunning Strike", "Deflect Missiles"],
            "special": ["Ki Focus"]
        },
        "sorcerer": {
            "passive": ["Magical Heritage", "Elemental Affinity"],
            "active": ["Wild Magic", "Metamagic", "Arcane Blast"],
            "special": ["Sorcerous Origin"]
        }
    }
    
    # Merge basic abilities with class-specific ones
    char_class = character_class.lower()
    result = basic_abilities.copy()
    
    if char_class in class_abilities:
        class_specific = class_abilities[char_class]
        for key in result:
            if key in class_specific:
                result[key].extend(class_specific[key])
    
    return result


def get_starter_inventory(character_class: str) -> List[Dict[str, Any]]:
    """
    Get starter inventory items based on character class.
    
    Args:
        character_class: The character's class
        
    Returns:
        List of inventory items
    """
    # Common items for all classes
    common_items = [
        {"name": "Backpack", "type": "gear", "value": 2, "description": "A leather backpack for storing items"},
        {"name": "Rations (1 day)", "type": "consumable", "value": 1, "quantity": 3, "description": "Food for one day"},
        {"name": "Water Flask", "type": "gear", "value": 1, "description": "A leather flask for water"},
    ]
    
    # Class-specific starting items
    class_items = {
        "warrior": [
            {"name": "Longsword", "type": "weapon", "damage": "1d8", "value": 15, "description": "Standard warrior weapon"},
            {"name": "Chain Mail", "type": "armor", "defense": 5, "value": 30, "description": "Metal armor offering good protection"},
            {"name": "Shield", "type": "armor", "defense": 2, "value": 10, "description": "A wooden shield with metal rim"}
        ],
        "wizard": [
            {"name": "Wizard Staff", "type": "weapon", "damage": "1d6", "value": 10, "description": "Focuses magical energy"},
            {"name": "Spellbook", "type": "gear", "value": 25, "description": "Contains your known spells"},
            {"name": "Mana Potion", "type": "consumable", "value": 15, "quantity": 2, "description": "Restores magical energy"}
        ],
        "rogue": [
            {"name": "Dagger", "type": "weapon", "damage": "1d4", "value": 5, "quantity": 2, "description": "Small, concealable blade"},
            {"name": "Leather Armor", "type": "armor", "defense": 3, "value": 15, "description": "Light, flexible protection"},
            {"name": "Lockpick Set", "type": "tool", "value": 20, "description": "Tools for opening locks"}
        ],
        "cleric": [
            {"name": "Mace", "type": "weapon", "damage": "1d6", "value": 12, "description": "Blunt weapon favored by clerics"},
            {"name": "Holy Symbol", "type": "gear", "value": 25, "description": "Symbol of your deity"},
            {"name": "Healing Potion", "type": "consumable", "value": 20, "quantity": 2, "description": "Restores health"}
        ],
        "bard": [
            {"name": "Rapier", "type": "weapon", "damage": "1d6", "value": 15, "description": "Elegant, precise blade"},
            {"name": "Lute", "type": "gear", "value": 30, "description": "Musical instrument for performances"},
            {"name": "Fine Clothes", "type": "gear", "value": 15, "description": "Impressive outfit for performances"}
        ]
    }
    
    # Create full inventory list
    inventory = common_items.copy()
    char_class = character_class.lower()
    
    if char_class in class_items:
        inventory.extend(class_items[char_class])
    else:
        # Generic equipment for classes not specifically defined
        inventory.extend([
            {"name": "Simple Weapon", "type": "weapon", "damage": "1d6", "value": 10, "description": "Standard weapon"},
            {"name": "Basic Outfit", "type": "gear", "defense": 1, "value": 5, "description": "Simple protective clothing"}
        ])
    
    return inventory


# Character progression defaults
def get_level_xp_requirements() -> Dict[int, int]:
    """
    Get the XP requirements for each level.
    
    Returns:
        Dictionary of level to XP requirement
    """
    # Base level XP requirements (follows exponential growth)
    level_requirements = {
        1: 0,       # Starting level
        2: 1000,    # 1000 XP to reach level 2
        3: 3000,    # 2000 more XP to reach level 3
        4: 6000,    # 3000 more XP to reach level 4
        5: 10000,   # 4000 more XP to reach level 5
        6: 15000,   # 5000 more XP to reach level 6
        7: 21000,   # 6000 more XP to reach level 7
        8: 28000,   # 7000 more XP to reach level 8
        9: 36000,   # 8000 more XP to reach level 9
        10: 45000,  # 9000 more XP to reach level 10
        11: 55000,  # 10000 more XP to reach level 11
        12: 66000,  # 11000 more XP to reach level 12
        13: 78000,  # 12000 more XP to reach level 13
        14: 91000,  # 13000 more XP to reach level 14
        15: 105000, # 14000 more XP to reach level 15
        16: 120000, # 15000 more XP to reach level 16
        17: 136000, # 16000 more XP to reach level 17
        18: 153000, # 17000 more XP to reach level 18
        19: 171000, # 18000 more XP to reach level 19
        20: 190000, # 19000 more XP to reach level 20
    }
    
    return level_requirements


def get_class_level_bonuses() -> Dict[str, Dict[int, Dict[str, Any]]]:
    """
    Get level-up bonuses for each class at different levels.
    
    Returns:
        Nested dictionary of class -> level -> bonuses
    """
    # Define bonuses for each class at each level
    class_bonuses = {
        "warrior": {
            2: {"abilities": ["Improved Combat Techniques"], "stats": {"strength": 1}},
            3: {"abilities": ["Battle Cry"], "stats": {"constitution": 1}},
            4: {"abilities": ["Second Wind"], "stats": {"strength": 1}},
            5: {"abilities": ["Extra Attack"], "stats": {"dexterity": 1, "strength": 1}},
            6: {"abilities": ["Defensive Stance"], "stats": {"constitution": 1}},
            7: {"abilities": ["Intimidating Presence"], "stats": {"strength": 1}},
            8: {"abilities": ["Improved Critical"], "stats": {"strength": 1, "constitution": 1}},
            9: {"abilities": ["Cleave"], "stats": {"strength": 1}},
            10: {"abilities": ["Champion's Might"], "stats": {"strength": 2, "constitution": 1}},
        },
        "wizard": {
            2: {"abilities": ["Arcane Recovery"], "stats": {"intelligence": 1}},
            3: {"abilities": ["Spell School Specialization"], "stats": {"intelligence": 1}},
            4: {"abilities": ["Cantrip Mastery"], "stats": {"intelligence": 1}},
            5: {"abilities": ["3rd Level Spells"], "stats": {"intelligence": 1, "wisdom": 1}},
            6: {"abilities": ["Arcane Tradition Feature"], "stats": {"intelligence": 1}},
            7: {"abilities": ["4th Level Spells"], "stats": {"intelligence": 1}},
            8: {"abilities": ["Ability Score Improvement"], "stats": {"intelligence": 2}},
            9: {"abilities": ["5th Level Spells"], "stats": {"intelligence": 1}},
            10: {"abilities": ["Arcane Mastery"], "stats": {"intelligence": 1, "wisdom": 1}},
        },
        "rogue": {
            2: {"abilities": ["Cunning Action"], "stats": {"dexterity": 1}},
            3: {"abilities": ["Roguish Archetype"], "stats": {"dexterity": 1}},
            4: {"abilities": ["Uncanny Dodge"], "stats": {"dexterity": 1}},
            5: {"abilities": ["Evasion"], "stats": {"dexterity": 1}},
            6: {"abilities": ["Expertise"], "stats": {"dexterity": 1}},
            7: {"abilities": ["Advanced Sneak Attack"], "stats": {"dexterity": 1}},
            8: {"abilities": ["Ability Score Improvement"], "stats": {"dexterity": 1, "charisma": 1}},
            9: {"abilities": ["Improved Reflexes"], "stats": {"dexterity": 1}},
            10: {"abilities": ["Shadow Master"], "stats": {"dexterity": 2}},
        },
        "cleric": {
            2: {"abilities": ["Channel Divinity"], "stats": {"wisdom": 1}},
            3: {"abilities": ["2nd Level Spells"], "stats": {"wisdom": 1}},
            4: {"abilities": ["Divine Domain Feature"], "stats": {"wisdom": 1}},
            5: {"abilities": ["3rd Level Spells"], "stats": {"wisdom": 1, "charisma": 1}},
            6: {"abilities": ["Improved Healing"], "stats": {"wisdom": 1}},
            7: {"abilities": ["4th Level Spells"], "stats": {"wisdom": 1}},
            8: {"abilities": ["Divine Strike"], "stats": {"wisdom": 1, "constitution": 1}},
            9: {"abilities": ["5th Level Spells"], "stats": {"wisdom": 1}},
            10: {"abilities": ["Divine Intervention"], "stats": {"wisdom": 2}},
        },
        "bard": {
            2: {"abilities": ["Jack of All Trades"], "stats": {"charisma": 1}},
            3: {"abilities": ["Bard College"], "stats": {"charisma": 1}},
            4: {"abilities": ["Expertise"], "stats": {"charisma": 1}},
            5: {"abilities": ["Font of Inspiration"], "stats": {"charisma": 1, "dexterity": 1}},
            6: {"abilities": ["Countercharm"], "stats": {"charisma": 1}},
            7: {"abilities": ["Bard College Feature"], "stats": {"charisma": 1}},
            8: {"abilities": ["Ability Score Improvement"], "stats": {"charisma": 1, "intelligence": 1}},
            9: {"abilities": ["Song of Rest Improvement"], "stats": {"charisma": 1}},
            10: {"abilities": ["Magical Secrets"], "stats": {"charisma": 2}},
        },
        "ranger": {
            2: {"abilities": ["Fighting Style"], "stats": {"dexterity": 1}},
            3: {"abilities": ["Ranger Conclave"], "stats": {"wisdom": 1}},
            4: {"abilities": ["Primeval Awareness"], "stats": {"dexterity": 1}},
            5: {"abilities": ["Extra Attack"], "stats": {"dexterity": 1, "wisdom": 1}},
            6: {"abilities": ["Greater Favored Enemy"], "stats": {"dexterity": 1}},
            7: {"abilities": ["Ranger Conclave Feature"], "stats": {"wisdom": 1}},
            8: {"abilities": ["Land's Stride"], "stats": {"dexterity": 1, "wisdom": 1}},
            9: {"abilities": ["Hide in Plain Sight"], "stats": {"dexterity": 1}},
            10: {"abilities": ["Nature's Warden"], "stats": {"wisdom": 2}},
        },
        "paladin": {
            2: {"abilities": ["Divine Smite"], "stats": {"strength": 1}},
            3: {"abilities": ["Sacred Oath"], "stats": {"charisma": 1}},
            4: {"abilities": ["Divine Health"], "stats": {"constitution": 1}},
            5: {"abilities": ["Extra Attack"], "stats": {"strength": 1, "charisma": 1}},
            6: {"abilities": ["Aura of Protection"], "stats": {"charisma": 1}},
            7: {"abilities": ["Sacred Oath Feature"], "stats": {"strength": 1}},
            8: {"abilities": ["Aura of Courage"], "stats": {"charisma": 1, "wisdom": 1}},
            9: {"abilities": ["Divine Sense Improvement"], "stats": {"charisma": 1}},
            10: {"abilities": ["Aura of Devotion"], "stats": {"charisma": 2}},
        },
        "druid": {
            2: {"abilities": ["Wild Shape"], "stats": {"wisdom": 1}},
            3: {"abilities": ["Druid Circle"], "stats": {"wisdom": 1}},
            4: {"abilities": ["Wild Shape Improvement"], "stats": {"wisdom": 1}},
            5: {"abilities": ["3rd Level Spells"], "stats": {"wisdom": 1, "constitution": 1}},
            6: {"abilities": ["Druid Circle Feature"], "stats": {"wisdom": 1}},
            7: {"abilities": ["4th Level Spells"], "stats": {"wisdom": 1}},
            8: {"abilities": ["Wild Shape Improvement"], "stats": {"wisdom": 1, "constitution": 1}},
            9: {"abilities": ["5th Level Spells"], "stats": {"wisdom": 1}},
            10: {"abilities": ["Nature's Sanctuary"], "stats": {"wisdom": 2}},
        },
        "monk": {
            2: {"abilities": ["Ki"], "stats": {"dexterity": 1}},
            3: {"abilities": ["Monastic Tradition"], "stats": {"wisdom": 1}},
            4: {"abilities": ["Slow Fall"], "stats": {"dexterity": 1}},
            5: {"abilities": ["Stunning Strike"], "stats": {"dexterity": 1, "wisdom": 1}},
            6: {"abilities": ["Ki-Empowered Strikes"], "stats": {"dexterity": 1}},
            7: {"abilities": ["Evasion"], "stats": {"dexterity": 1}},
            8: {"abilities": ["Stillness of Mind"], "stats": {"wisdom": 1, "dexterity": 1}},
            9: {"abilities": ["Unarmored Movement Improvement"], "stats": {"dexterity": 1}},
            10: {"abilities": ["Purity of Body"], "stats": {"constitution": 1, "wisdom": 1}},
        },
        "sorcerer": {
            2: {"abilities": ["Font of Magic"], "stats": {"charisma": 1}},
            3: {"abilities": ["Metamagic"], "stats": {"charisma": 1}},
            4: {"abilities": ["Sorcerous Origin Feature"], "stats": {"charisma": 1}},
            5: {"abilities": ["3rd Level Spells"], "stats": {"charisma": 1, "constitution": 1}},
            6: {"abilities": ["Additional Metamagic"], "stats": {"charisma": 1}},
            7: {"abilities": ["4th Level Spells"], "stats": {"charisma": 1}},
            8: {"abilities": ["Ability Score Improvement"], "stats": {"charisma": 1, "constitution": 1}},
            9: {"abilities": ["5th Level Spells"], "stats": {"charisma": 1}},
            10: {"abilities": ["Sorcerous Restoration"], "stats": {"charisma": 2}},
        },
    }
    
    return class_bonuses


def get_xp_reward_values() -> Dict[str, Dict[str, int]]:
    """
    Get standard XP rewards for different types of actions.
    
    Returns:
        Dictionary of action types and their XP values for different difficulty levels
    """
    # Define XP rewards for different action types and difficulties
    xp_rewards = {
        "combat": {
            "easy": 100,
            "medium": 200,
            "hard": 400,
            "boss": 1000
        },
        "quest": {
            "minor": 300,
            "standard": 600,
            "major": 1200,
            "epic": 2500
        },
        "puzzle": {
            "easy": 150,
            "medium": 300,
            "hard": 600
        },
        "exploration": {
            "location": 100,
            "secret": 200,
            "landmark": 300
        },
        "roleplay": {
            "minor": 50,
            "significant": 150,
            "major": 300
        },
        "crafting": {
            "basic": 50,
            "advanced": 150,
            "masterwork": 300
        }
    }
    
    return xp_rewards
