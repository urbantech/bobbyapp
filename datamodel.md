```mermaid
classDiagram
    class User {
        +UUID user_id
        +String username
        +String email
        +String password_hash
        +String subscription_level
        +DateTime created_at
        +create_character()
        +interact_with_character()
        +roll_dice()
        +start_quest()
    }

    class Character {
        +UUID character_id
        +String name
        +String class
        +Text backstory
        +JSONB personality
        +JSONB stats
        +JSONB inventory
        +Integer level
        +Integer health
        +JSONB abilities
        +UUID created_by [FK]
        +respond_to_user()
        +engage_in_conversation()
        +participate_in_combat()
        +remember_past_interactions()
    }

    class Conversation {
        +UUID conversation_id
        +UUID user_id [FK]
        +UUID character_id [FK]
        +JSONB messages
        +DateTime timestamp
        +add_message()
        +retrieve_context()
        +analyze_tone()
    }

    class Quest {
        +UUID quest_id
        +String name
        +Text description
        +String difficulty
        +JSONB reward
        +Enum status (Pending, Completed, Failed)
        +UUID assigned_to [FK]
        +start_quest()
        +complete_quest()
        +fail_quest()
    }

    class DiceRoll {
        +UUID roll_id
        +UUID user_id [FK]
        +UUID character_id [FK]
        +Integer dice_type
        +Integer result
        +DateTime timestamp
        +roll_dice()
        +validate_roll()
    }

    class MultimodalData {
        +UUID data_id
        +UUID conversation_id [FK]
        +Enum type (Text, Voice, Image, Animation)
        +String content_url
        +DateTime generated_at
        +retrieve_media()
        +generate_media()
    }

    User "1" -- "many" Character : creates
    User "1" -- "many" Conversation : initiates
    User "1" -- "many" Quest : assigned
    User "1" -- "many" DiceRoll : performs

    Character "1" -- "many" Conversation : participates
    Character "1" -- "many" Quest : assigned
    Character "1" -- "many" DiceRoll : engages

    Conversation "1" -- "many" MultimodalData : stores




### **How to Use This Markdown UML Model**
- If you're using **GitHub**, simply copy and paste the code into a markdown (`.md`) file—GitHub automatically renders **Mermaid diagrams**.
- If you want to preview this locally, you can use **VS Code** with the [Markdown Preview Mermaid Support](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid) extension.
- Online tools like [Mermaid Live Editor](https://mermaid-js.github.io/mermaid-live/) can also render this model.

Let me know if you need modifications! 🚀

