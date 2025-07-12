import discord
import random
import math
from typing import Union, List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def create_embed(title: str, description: str, color: discord.Color = discord.Color.blue()) -> discord.Embed:
    """Create a standardized embed."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    return embed

def format_number(number: Union[int, float]) -> str:
    """Format numbers with commas for readability."""
    if isinstance(number, float):
        return f"{number:,.2f}"
    return f"{number:,}"

def create_progress_bar(percentage: float, length: int = 10) -> str:
    """Create a progress bar string."""
    filled = int(percentage / 100 * length)
    empty = length - filled
    bar = "█" * filled + "░" * empty
    return f"`{bar}` {percentage:.1f}%"

def calculate_xp_for_level(level: int) -> int:
    """Calculate XP required for a specific level."""
    if level <= 1:
        return 100
    return int(100 * (level ** 1.5))

def calculate_level_from_xp(xp: int) -> int:
    """Calculate level from total XP."""
    if xp < 100:
        return 1
    
    # Binary search for efficiency
    left, right = 1, 100
    while left < right:
        mid = (left + right + 1) // 2
        if calculate_xp_for_level(mid) <= xp:
            left = mid
        else:
            right = mid - 1
    
    return left

def level_up_player(player_data: Dict[str, Any]) -> str:
    """Level up a player and return level up message."""
    try:
        old_level = player_data['level']
        
        while player_data['xp'] >= player_data['max_xp']:
            player_data['xp'] -= player_data['max_xp']
            player_data['level'] += 1
            
            # Increase stats
            hp_increase = random.randint(15, 25)
            attack_increase = random.randint(2, 5)
            defense_increase = random.randint(1, 3)
            
            player_data['max_hp'] += hp_increase
            player_data['hp'] = player_data['max_hp']  # Full heal on level up
            player_data['attack'] += attack_increase
            player_data['defense'] += defense_increase
            
            # Calculate new XP requirement
            player_data['max_xp'] = calculate_xp_for_level(player_data['level'])
        
        levels_gained = player_data['level'] - old_level
        if levels_gained > 0:
            return (f"🎉 **Level Up!** You are now level {player_data['level']}!\n"
                    f"**New Stats:**\n"
                    f"HP: {player_data['hp']}/{player_data['max_hp']}\n"
                    f"Attack: {player_data['attack']}\n"
                    f"Defense: {player_data['defense']}")
        
        return ""
    except Exception as e:
        logger.error(f"Error leveling up player: {e}")
        return ""

def get_random_adventure_outcome() -> Dict[str, Any]:
    """Get a random adventure outcome."""
    outcomes = [
        {
            "type": "treasure",
            "weight": 30,
            "min_coins": 20,
            "max_coins": 80,
            "min_xp": 10,
            "max_xp": 30,
            "description": "💰 You discovered a treasure chest!"
        },
        {
            "type": "monster",
            "weight": 25,
            "min_coins": 30,
            "max_coins": 100,
            "min_xp": 20,
            "max_xp": 40,
            "description": "⚔️ You encountered a monster!"
        },
        {
            "type": "merchant",
            "weight": 20,
            "min_coins": 15,
            "max_coins": 50,
            "min_xp": 8,
            "max_xp": 25,
            "description": "🏪 You met a traveling merchant!"
        },
        {
            "type": "mystery",
            "weight": 15,
            "min_coins": 40,
            "max_coins": 120,
            "min_xp": 15,
            "max_xp": 35,
            "description": "🔮 You solved a mysterious puzzle!"
        },
        {
            "type": "rare_find",
            "weight": 10,
            "min_coins": 60,
            "max_coins": 150,
            "min_xp": 25,
            "max_xp": 50,
            "description": "✨ You made a rare discovery!"
        }
    ]
    
    return random.choices(outcomes, weights=[o["weight"] for o in outcomes])[0]

def get_random_work_job() -> Dict[str, Any]:
    """Get a random work job."""
    jobs = [
        {
            "name": "Blacksmith",
            "min_coins": 80,
            "max_coins": 150,
            "min_xp": 5,
            "max_xp": 15,
            "description": "⚒️ You worked as a blacksmith, forging weapons and armor."
        },
        {
            "name": "Merchant",
            "min_coins": 60,
            "max_coins": 120,
            "min_xp": 3,
            "max_xp": 10,
            "description": "🏪 You worked as a merchant, buying and selling goods."
        },
        {
            "name": "Guard",
            "min_coins": 70,
            "max_coins": 140,
            "min_xp": 4,
            "max_xp": 12,
            "description": "🛡️ You worked as a guard, protecting the city."
        },
        {
            "name": "Farmer",
            "min_coins": 50,
            "max_coins": 100,
            "min_xp": 2,
            "max_xp": 8,
            "description": "🌾 You worked as a farmer, tending to crops."
        },
        {
            "name": "Miner",
            "min_coins": 90,
            "max_coins": 180,
            "min_xp": 6,
            "max_xp": 18,
            "description": "⛏️ You worked as a miner, extracting precious resources."
        },
        {
            "name": "Fisher",
            "min_coins": 40,
            "max_coins": 90,
            "min_xp": 2,
            "max_xp": 7,
            "description": "🎣 You worked as a fisher, catching fish by the river."
        },
        {
            "name": "Hunter",
            "min_coins": 85,
            "max_coins": 160,
            "min_xp": 5,
            "max_xp": 16,
            "description": "🏹 You worked as a hunter, tracking down wild game."
        }
    ]
    
    return random.choice(jobs)

def get_time_until_next_use(last_use_time: str, cooldown_seconds: int) -> int:
    """Get seconds until next use of a cooldown command."""
    try:
        if not last_use_time:
            return 0
        
        last_use = datetime.fromisoformat(last_use_time)
        now = datetime.now()
        elapsed = (now - last_use).total_seconds()
        
        if elapsed >= cooldown_seconds:
            return 0
        
        return int(cooldown_seconds - elapsed)
    except Exception as e:
        logger.error(f"Error calculating time until next use: {e}")
        return 0

def format_time_remaining(seconds: int) -> str:
    """Format seconds into a readable time string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}m {seconds}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def get_user_mention_from_id(user_id: str) -> str:
    """Convert user ID to mention format."""
    return f"<@{user_id}>"

def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def get_random_color() -> discord.Color:
    """Get a random Discord color."""
    colors = [
        discord.Color.red(),
        discord.Color.orange(),
        discord.Color.gold(),
        discord.Color.green(),
        discord.Color.blue(),
        discord.Color.purple(),
        discord.Color.magenta(),
        discord.Color.teal()
    ]
    return random.choice(colors)

def calculate_coin_multiplier(level: int) -> float:
    """Calculate coin multiplier based on level."""
    return 1.0 + (level - 1) * 0.1

def get_rarity_color(rarity: str) -> discord.Color:
    """Get color based on item rarity."""
    rarity_colors = {
        'common': discord.Color.light_grey(),
        'uncommon': discord.Color.green(),
        'rare': discord.Color.blue(),
        'epic': discord.Color.purple(),
        'legendary': discord.Color.gold()
    }
    return rarity_colors.get(rarity.lower(), discord.Color.light_grey())

def validate_user_input(input_str: str, max_length: int = 100) -> bool:
    """Validate user input for safety."""
    if not input_str or len(input_str) > max_length:
        return False
    
    # Check for potentially harmful content
    forbidden_chars = ['<', '>', '@', '&', '#']
    return not any(char in input_str for char in forbidden_chars)

def safe_divide(numerator: Union[int, float], denominator: Union[int, float]) -> float:
    """Safely divide two numbers, return 0 if denominator is 0."""
    try:
        if denominator == 0:
            return 0.0
        return numerator / denominator
    except:
        return 0.0

def clamp(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))
