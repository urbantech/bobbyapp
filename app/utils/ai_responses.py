"""
Utility functions for generating AI responses.
This module will be expanded in future sprints to integrate with LLMs.
For now, it provides simple responses for testing.
"""

import random
from typing import Dict, Any, List


def get_character_response(
    character: Dict[str, Any], 
    user_message: str,
    conversation_history: List[Dict[str, Any]] = None
) -> str:
    """
    Generate a response from a character based on user input and conversation history.
    
    In future sprints, this will be connected to an LLM like:
    - Local model via Ollama
    - OpenAI API
    - Anthropic API
    
    Args:
        character: Character data dictionary
        user_message: The user's message to respond to
        conversation_history: Optional list of previous messages
        
    Returns:
        A string response from the character
    """
    # Simple response for testing purposes
    # In a real implementation, this would use an LLM
    
    # Character traits influence response
    personality = character.get("personality", {})
    traits = personality.get("traits", [])
    
    # Character class influences response style
    char_class = character.get("character_class", "").lower()
    
    # Simple keyword-based responses for testing
    greeting_keywords = ["hello", "hi", "hey", "greetings", "howdy"]
    question_keywords = ["?", "who", "what", "where", "when", "why", "how"]
    
    # Greeting responses
    if any(keyword in user_message.lower() for keyword in greeting_keywords):
        greetings = [
            f"Greetings, traveler. I am {character['name']}.",
            f"Well met! I am {character['name']}, a {char_class}.",
            f"Hello there! {character['name']} at your service."
        ]
        return random.choice(greetings)
    
    # Question responses
    elif any(keyword in user_message.lower() for keyword in question_keywords):
        if "you" in user_message.lower():
            # Questions about the character
            return f"I am {character['name']}, a {char_class}. {character.get('backstory', '')[:100]}..."
        else:
            # General questions
            responses = [
                "That's an interesting question. Let me think...",
                "I've pondered that matter before.",
                "A good question deserves a thoughtful answer."
            ]
            return random.choice(responses) + " " + generate_response_by_class(char_class)
    
    # Combat-related responses
    elif any(word in user_message.lower() for word in ["fight", "battle", "combat", "attack"]):
        combat_responses = {
            "warrior": "I live for battle! My sword is ready.",
            "wizard": "I prefer to solve problems with magic, but I can defend myself if needed.",
            "rogue": "I prefer stealth, but I can certainly handle myself in a fight.",
            "cleric": "Violence is not always the answer, but I will defend what is right.",
            "bard": "I may not look like a fighter, but I've survived my share of scrapes.",
            "default": "I'm prepared to face any challenge that comes my way."
        }
        return combat_responses.get(char_class, combat_responses["default"])
    
    # Default responses based on traits
    elif traits:
        trait = random.choice(traits)
        return generate_response_by_trait(trait, character['name'])
    
    # Generic fallback responses
    else:
        generic_responses = [
            f"I see. Tell me more about that.",
            f"Interesting perspective. As a {char_class}, I have unique insights on such matters.",
            f"That's worth considering. In my journeys, I've learned many things.",
            f"Indeed. What else is on your mind, traveler?"
        ]
        return random.choice(generic_responses)


def generate_response_by_class(character_class: str) -> str:
    """Generate a response influenced by character class"""
    class_responses = {
        "warrior": "I approach problems directly, with strength and honor.",
        "wizard": "I see patterns where others see chaos. Knowledge is true power.",
        "rogue": "Sometimes the best approach isn't the most obvious one.",
        "cleric": "I seek to understand the divine purpose in all things.",
        "bard": "Life is a story worth telling, with many twists and turns.",
        "ranger": "I've learned much from observing nature and its ways.",
        "paladin": "I'm guided by a strong moral code in all my actions.",
        "druid": "Nature has wisdom to teach those who will listen.",
        "monk": "Inner peace leads to outer strength. Balance in all things.",
        "sorcerer": "Magic flows through me naturally, like breathing.",
    }
    return class_responses.get(character_class, "I have my own way of seeing the world.")


def generate_response_by_trait(trait: str, name: str) -> str:
    """Generate a response influenced by a personality trait"""
    trait_responses = {
        "brave": f"I, {name}, have never backed down from a challenge.",
        "wise": "I've learned that wisdom comes from listening more than speaking.",
        "curious": "That fascinates me! I always seek to learn more about the world.",
        "cautious": "We should proceed carefully. I prefer to know what I'm getting into.",
        "honorable": "My word is my bond. I live by a code of honor.",
        "mysterious": "There are some secrets I keep, even from my closest allies.",
        "playful": "Life is too short not to find joy in the journey!",
        "serious": "Some matters deserve our full attention and respect.",
        "loyal": "Once you have my friendship, you have my unwavering support.",
        "ambitious": "I have great plans. This is just one step on my path.",
        "kind": "I believe in showing compassion to all creatures.",
        "stern": "Discipline and focus are essential for success.",
        "charming": "I've found that a well-placed compliment opens many doors.",
    }
    return trait_responses.get(trait.lower(), f"As {name}, I follow my own path.")
