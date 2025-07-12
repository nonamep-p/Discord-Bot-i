import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from utils.database import get_user_data, update_user_data
import logging

logger = logging.getLogger(__name__)

class RNGSystem:
    """Advanced RNG system with hidden conditions and lucky events."""
    
    def __init__(self):
        self.luck_multipliers = {
            "cursed": 0.5,
            "unlucky": 0.75,
            "normal": 1.0,
            "lucky": 1.25,
            "blessed": 1.5,
            "divine": 2.0
        }
        
        # Hidden conditions that affect luck
        self.hidden_conditions = {
            "full_moon": {"chance": 0.03, "luck_boost": 0.3, "duration": 24},  # 3% chance per day
            "lucky_streak": {"threshold": 3, "luck_boost": 0.5, "duration": 6},  # After 3 lucky events
            "midnight_blessing": {"hour": 0, "luck_boost": 0.4, "duration": 1},  # Only at midnight
            "prime_time": {"hours": [7, 11, 13, 17, 19], "luck_boost": 0.2, "duration": 1},  # Prime numbers
            "lucky_number": {"numbers": [7, 13, 21, 42, 777], "luck_boost": 0.6, "duration": 12}
        }
        
        # Rare events that can trigger
        self.rare_events = {
            "treasure_chest": {"base_chance": 0.001, "rewards": {"coins": (500, 2000), "xp": (100, 500)}},
            "mysterious_merchant": {"base_chance": 0.0005, "special_items": True},
            "ancient_relic": {"base_chance": 0.0001, "legendary_item": True},
            "dragon_blessing": {"base_chance": 0.00005, "permanent_luck": True},
            "time_anomaly": {"base_chance": 0.00001, "double_rewards": True}
        }

    def get_user_luck_state(self, user_id: int) -> Dict:
        """Get user's current luck state."""
        user_data = get_user_data(user_id)
        return user_data.get('luck_state', {
            'base_luck': 1.0,
            'active_conditions': [],
            'lucky_streak': 0,
            'rare_events_found': [],
            'last_luck_check': 0
        })

    def update_user_luck_state(self, user_id: int, luck_state: Dict):
        """Update user's luck state."""
        user_data = get_user_data(user_id)
        user_data['luck_state'] = luck_state
        update_user_data(user_id, user_data)

    def check_hidden_conditions(self, user_id: int) -> List[str]:
        """Check for active hidden conditions."""
        current_time = datetime.now()
        active_conditions = []
        
        # Full moon condition (random chance)
        if random.random() < self.hidden_conditions["full_moon"]["chance"]:
            active_conditions.append("full_moon")
        
        # Midnight blessing
        if current_time.hour == self.hidden_conditions["midnight_blessing"]["hour"]:
            active_conditions.append("midnight_blessing")
        
        # Prime time hours
        if current_time.hour in self.hidden_conditions["prime_time"]["hours"]:
            active_conditions.append("prime_time")
        
        # Lucky number condition (based on user ID digits)
        user_digits = sum(int(digit) for digit in str(user_id))
        if user_digits in self.hidden_conditions["lucky_number"]["numbers"]:
            active_conditions.append("lucky_number")
        
        return active_conditions

    def calculate_luck_multiplier(self, user_id: int) -> Tuple[float, List[str]]:
        """Calculate total luck multiplier for user."""
        luck_state = self.get_user_luck_state(user_id)
        base_luck = luck_state.get('base_luck', 1.0)
        
        # Check for hidden conditions
        active_conditions = self.check_hidden_conditions(user_id)
        
        # Check for lucky streak
        if luck_state.get('lucky_streak', 0) >= self.hidden_conditions["lucky_streak"]["threshold"]:
            active_conditions.append("lucky_streak")
        
        # Calculate total multiplier
        total_multiplier = base_luck
        condition_descriptions = []
        
        for condition in active_conditions:
            if condition in self.hidden_conditions:
                boost = self.hidden_conditions[condition]["luck_boost"]
                total_multiplier += boost
                condition_descriptions.append(self.get_condition_description(condition))
        
        return total_multiplier, condition_descriptions

    def get_condition_description(self, condition: str) -> str:
        """Get description for a luck condition."""
        descriptions = {
            "full_moon": "🌕 **Full Moon Blessing** - The moon's power guides your fortune",
            "lucky_streak": "🔥 **Lucky Streak** - Fortune favors the bold",
            "midnight_blessing": "🌙 **Midnight Blessing** - Dark magic enhances your luck",
            "prime_time": "⚡ **Prime Time** - The numbers align in your favor",
            "lucky_number": "🎲 **Lucky Numbers** - Your destiny is written in digits"
        }
        return descriptions.get(condition, f"✨ **{condition.title()}** - Mysterious forces aid you")

    def roll_with_luck(self, user_id: int, base_chance: float, event_type: str = "general") -> Tuple[bool, Dict]:
        """Roll with luck multiplier applied."""
        luck_multiplier, active_conditions = self.calculate_luck_multiplier(user_id)
        
        # Apply luck to the roll
        modified_chance = min(base_chance * luck_multiplier, 0.95)  # Cap at 95%
        
        roll_result = random.random()
        success = roll_result <= modified_chance
        
        # Update luck state
        luck_state = self.get_user_luck_state(user_id)
        if success:
            luck_state['lucky_streak'] = luck_state.get('lucky_streak', 0) + 1
        else:
            luck_state['lucky_streak'] = max(0, luck_state.get('lucky_streak', 0) - 1)
        
        luck_state['last_luck_check'] = time.time()
        self.update_user_luck_state(user_id, luck_state)
        
        return success, {
            'luck_multiplier': luck_multiplier,
            'active_conditions': active_conditions,
            'modified_chance': modified_chance,
            'roll_result': roll_result,
            'lucky_streak': luck_state['lucky_streak']
        }

    def check_rare_event(self, user_id: int) -> Optional[Dict]:
        """Check if a rare event occurs."""
        luck_multiplier, _ = self.calculate_luck_multiplier(user_id)
        
        for event_name, event_data in self.rare_events.items():
            base_chance = event_data["base_chance"]
            modified_chance = base_chance * luck_multiplier
            
            if random.random() <= modified_chance:
                # Record the rare event
                luck_state = self.get_user_luck_state(user_id)
                rare_events = luck_state.get('rare_events_found', [])
                if event_name not in rare_events:
                    rare_events.append(event_name)
                    luck_state['rare_events_found'] = rare_events
                    self.update_user_luck_state(user_id, luck_state)
                
                return {
                    'event_name': event_name,
                    'event_data': event_data,
                    'luck_multiplier': luck_multiplier,
                    'is_first_time': event_name not in luck_state.get('rare_events_found', [])
                }
        
        return None

    def generate_rare_event_reward(self, event_name: str, user_level: int) -> Dict:
        """Generate rewards for rare events."""
        event_data = self.rare_events.get(event_name, {})
        rewards = {}
        
        if event_name == "treasure_chest":
            coin_range = event_data["rewards"]["coins"]
            xp_range = event_data["rewards"]["xp"]
            rewards = {
                "coins": random.randint(coin_range[0], coin_range[1]) * max(1, user_level // 5),
                "xp": random.randint(xp_range[0], xp_range[1]) * max(1, user_level // 3),
                "description": "💰 **Treasure Chest Found!** - Ancient riches await the worthy!"
            }
        
        elif event_name == "mysterious_merchant":
            rare_items = ["Phoenix Feather", "Dragon Scale", "Moonstone", "Star Fragment", "Void Crystal"]
            selected_item = random.choice(rare_items)
            rewards = {
                "special_item": selected_item,
                "description": f"🧙‍♂️ **Mysterious Merchant** - Offers you a rare {selected_item}!"
            }
        
        elif event_name == "ancient_relic":
            legendary_items = ["Excalibur", "Mjolnir", "Aegis Shield", "Ring of Power", "Crown of Kings"]
            selected_item = random.choice(legendary_items)
            rewards = {
                "legendary_item": selected_item,
                "permanent_stats": {"attack": 50, "defense": 50, "hp": 100},
                "description": f"🏛️ **Ancient Relic Discovered!** - The legendary {selected_item} is yours!"
            }
        
        elif event_name == "dragon_blessing":
            rewards = {
                "permanent_luck_boost": 0.25,
                "title": "Dragon-Blessed",
                "description": "🐉 **Dragon's Blessing** - Your luck is forever enhanced by ancient dragon magic!"
            }
        
        elif event_name == "time_anomaly":
            rewards = {
                "double_rewards_duration": 24,  # 24 hours
                "description": "⏰ **Time Anomaly** - Reality bends around you, doubling all rewards for 24 hours!"
            }
        
        return rewards

    def get_luck_status_embed_data(self, user_id: int) -> Dict:
        """Get data for luck status embed."""
        luck_multiplier, active_conditions = self.calculate_luck_multiplier(user_id)
        luck_state = self.get_user_luck_state(user_id)
        
        # Determine luck tier
        luck_tier = "normal"
        if luck_multiplier >= 2.0:
            luck_tier = "divine"
        elif luck_multiplier >= 1.5:
            luck_tier = "blessed"
        elif luck_multiplier >= 1.25:
            luck_tier = "lucky"
        elif luck_multiplier <= 0.5:
            luck_tier = "cursed"
        elif luck_multiplier <= 0.75:
            luck_tier = "unlucky"
        
        return {
            "luck_multiplier": luck_multiplier,
            "luck_tier": luck_tier,
            "active_conditions": active_conditions,
            "lucky_streak": luck_state.get('lucky_streak', 0),
            "rare_events_found": luck_state.get('rare_events_found', []),
            "total_rare_events": len(luck_state.get('rare_events_found', []))
        }

# Global RNG system instance
rng_system = RNGSystem()

# Convenience functions
def roll_with_luck(user_id: int, base_chance: float, event_type: str = "general") -> Tuple[bool, Dict]:
    """Roll with luck applied."""
    return rng_system.roll_with_luck(user_id, base_chance, event_type)

def check_rare_event(user_id: int) -> Optional[Dict]:
    """Check for rare events."""
    return rng_system.check_rare_event(user_id)

def get_luck_status(user_id: int) -> Dict:
    """Get user's luck status."""
    return rng_system.get_luck_status_embed_data(user_id)