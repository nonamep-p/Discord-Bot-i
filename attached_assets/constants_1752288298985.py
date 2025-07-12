# RPG Constants
RPG_CONSTANTS = {
    'max_level': 100,
    'base_xp': 100,
    'base_hp': 100,
    'base_attack': 10,
    'base_defense': 5,
    'starting_coins': 100,
    'max_inventory_size': 50,
    'adventure_cooldown': 300,  # 5 minutes
    'dungeon_cooldown': 600,    # 10 minutes
    'work_cooldown': 3600,      # 1 hour
    'daily_cooldown': 86400,    # 24 hours
    'heal_cooldown': 1800       # 30 minutes
}

# Item definitions
ITEMS = {
    'weapons': {
        'Wooden Sword': {
            'attack': 3,
            'price': 100,
            'rarity': 'common',
            'description': 'A basic wooden sword for beginners.'
        },
        'Iron Sword': {
            'attack': 8,
            'price': 500,
            'rarity': 'uncommon',
            'description': 'A sturdy iron sword with good balance.'
        },
        'Steel Sword': {
            'attack': 15,
            'price': 1500,
            'rarity': 'rare',
            'description': 'A sharp steel sword favored by warriors.'
        },
        'Enchanted Blade': {
            'attack': 25,
            'price': 5000,
            'rarity': 'epic',
            'description': 'A magically enhanced blade that glows with power.'
        },
        'Legendary Sword': {
            'attack': 40,
            'price': 15000,
            'rarity': 'legendary',
            'description': 'A legendary weapon of immense power.'
        }
    },
    'armor': {
        'Leather Armor': {
            'defense': 3,
            'price': 150,
            'rarity': 'common',
            'description': 'Basic leather armor for protection.'
        },
        'Iron Shield': {
            'defense': 6,
            'price': 600,
            'rarity': 'uncommon',
            'description': 'A solid iron shield for blocking attacks.'
        },
        'Steel Armor': {
            'defense': 12,
            'price': 2000,
            'rarity': 'rare',
            'description': 'Heavy steel armor for maximum protection.'
        },
        'Enchanted Mail': {
            'defense': 20,
            'price': 6000,
            'rarity': 'epic',
            'description': 'Magically protected mail armor.'
        },
        'Dragon Scale Armor': {
            'defense': 35,
            'price': 20000,
            'rarity': 'legendary',
            'description': 'Armor made from ancient dragon scales.'
        }
    },
    'consumables': {
        'Health Potion': {
            'heal': 50,
            'price': 25,
            'rarity': 'common',
            'description': 'Restores 50 HP when consumed.'
        },
        'Greater Health Potion': {
            'heal': 100,
            'price': 75,
            'rarity': 'uncommon',
            'description': 'Restores 100 HP when consumed.'
        },
        'Mana Potion': {
            'effect': 'mana',
            'price': 40,
            'rarity': 'common',
            'description': 'Restores magical energy.'
        },
        'Strength Potion': {
            'effect': 'strength',
            'price': 100,
            'rarity': 'uncommon',
            'description': 'Temporarily increases attack power.'
        },
        'Elixir of Power': {
            'effect': 'all_stats',
            'price': 500,
            'rarity': 'rare',
            'description': 'Temporarily boosts all stats.'
        }
    },
    'misc': {
        'Magic Ring': {
            'effect': 'permanent_stats',
            'price': 1000,
            'rarity': 'rare',
            'description': 'A magical ring that permanently increases stats.'
        },
        'Lucky Charm': {
            'effect': 'luck',
            'price': 250,
            'rarity': 'uncommon',
            'description': 'Increases luck in adventures.'
        },
        'Ancient Scroll': {
            'effect': 'xp_boost',
            'price': 300,
            'rarity': 'uncommon',
            'description': 'Provides bonus XP when used.'
        }
    }
}

# Shop items (available for purchase)
SHOP_ITEMS = {
    'weapons': {
        'Wooden Sword': ITEMS['weapons']['Wooden Sword'],
        'Iron Sword': ITEMS['weapons']['Iron Sword'],
        'Steel Sword': ITEMS['weapons']['Steel Sword']
    },
    'armor': {
        'Leather Armor': ITEMS['armor']['Leather Armor'],
        'Iron Shield': ITEMS['armor']['Iron Shield'],
        'Steel Armor': ITEMS['armor']['Steel Armor']
    },
    'consumables': {
        'Health Potion': ITEMS['consumables']['Health Potion'],
        'Greater Health Potion': ITEMS['consumables']['Greater Health Potion'],
        'Mana Potion': ITEMS['consumables']['Mana Potion'],
        'Strength Potion': ITEMS['consumables']['Strength Potion']
    },
    'misc': {
        'Lucky Charm': ITEMS['misc']['Lucky Charm'],
        'Ancient Scroll': ITEMS['misc']['Ancient Scroll']
    }
}

# Monster definitions
MONSTERS = {
    'common': [
        {'name': 'Goblin', 'hp': 30, 'attack': 8, 'defense': 2, 'xp': 15, 'coins': 20},
        {'name': 'Skeleton', 'hp': 25, 'attack': 10, 'defense': 3, 'xp': 18, 'coins': 25},
        {'name': 'Wolf', 'hp': 35, 'attack': 12, 'defense': 1, 'xp': 20, 'coins': 18},
        {'name': 'Bandit', 'hp': 40, 'attack': 15, 'defense': 4, 'xp': 25, 'coins': 35}
    ],
    'uncommon': [
        {'name': 'Orc', 'hp': 60, 'attack': 18, 'defense': 6, 'xp': 40, 'coins': 60},
        {'name': 'Troll', 'hp': 80, 'attack': 22, 'defense': 8, 'xp': 50, 'coins': 80},
        {'name': 'Dark Mage', 'hp': 45, 'attack': 25, 'defense': 5, 'xp': 45, 'coins': 70}
    ],
    'rare': [
        {'name': 'Minotaur', 'hp': 120, 'attack': 30, 'defense': 12, 'xp': 80, 'coins': 150},
        {'name': 'Wyvern', 'hp': 100, 'attack': 35, 'defense': 10, 'xp': 90, 'coins': 200},
        {'name': 'Lich', 'hp': 90, 'attack': 40, 'defense': 15, 'xp': 100, 'coins': 250}
    ],
    'boss': [
        {'name': 'Ancient Dragon', 'hp': 200, 'attack': 50, 'defense': 20, 'xp': 200, 'coins': 500},
        {'name': 'Demon Lord', 'hp': 250, 'attack': 60, 'defense': 25, 'xp': 300, 'coins': 750},
        {'name': 'Shadow King', 'hp': 180, 'attack': 55, 'defense': 18, 'xp': 250, 'coins': 600}
    ]
}

# Adventure locations
ADVENTURE_LOCATIONS = [
    'Whispering Woods',
    'Crystal Caves',
    'Misty Mountains',
    'Haunted Ruins',
    'Forgotten Temple',
    'Dragon\'s Lair',
    'Enchanted Forest',
    'Dark Swamp',
    'Golden Fields',
    'Frozen Tundra',
    'Sunken City',
    'Floating Islands',
    'Volcanic Crater',
    'Ancient Library',
    'Cursed Graveyard'
]

# Dungeon types
DUNGEON_TYPES = [
    'Ancient Tomb',
    'Abandoned Mine',
    'Cursed Castle',
    'Underground Labyrinth',
    'Wizard\'s Tower',
    'Demon\'s Fortress',
    'Crystal Caverns',
    'Shadow Realm',
    'Fire Temple',
    'Ice Palace',
    'Sunken Ruins',
    'Sky Citadel',
    'Bone Catacombs',
    'Elemental Sanctuary',
    'Time Vortex'
]

# Status effects
STATUS_EFFECTS = {
    'poisoned': {
        'duration': 3,
        'damage_per_turn': 5,
        'description': 'Taking poison damage each turn'
    },
    'blessed': {
        'duration': 5,
        'effect': 'double_xp',
        'description': 'Earning double XP'
    },
    'cursed': {
        'duration': 3,
        'effect': 'half_coins',
        'description': 'Earning half coins'
    },
    'strengthened': {
        'duration': 4,
        'effect': 'double_attack',
        'description': 'Attack power doubled'
    }
}

# Achievement definitions
ACHIEVEMENTS = {
    'first_steps': {
        'name': 'First Steps',
        'description': 'Complete your first adventure',
        'requirement': 'adventures_completed',
        'threshold': 1,
        'reward_coins': 100,
        'reward_xp': 50
    },
    'adventurer': {
        'name': 'Adventurer',
        'description': 'Complete 50 adventures',
        'requirement': 'adventures_completed',
        'threshold': 50,
        'reward_coins': 1000,
        'reward_xp': 500
    },
    'dungeon_delver': {
        'name': 'Dungeon Delver',
        'description': 'Complete 10 dungeons',
        'requirement': 'dungeons_completed',
        'threshold': 10,
        'reward_coins': 2000,
        'reward_xp': 1000
    },
    'wealthy': {
        'name': 'Wealthy',
        'description': 'Accumulate 10,000 coins',
        'requirement': 'coins',
        'threshold': 10000,
        'reward_coins': 5000,
        'reward_xp': 2000
    },
    'max_level': {
        'name': 'Legend',
        'description': 'Reach maximum level',
        'requirement': 'level',
        'threshold': 100,
        'reward_coins': 50000,
        'reward_xp': 0
    }
}

# Daily reward tiers
DAILY_REWARDS = {
    'base': 200,
    'level_multiplier': 50,
    'streak_bonuses': {
        7: 500,   # 1 week
        30: 2000, # 1 month
        365: 10000 # 1 year
    }
}

# Work job rarity and rewards
WORK_JOBS = {
    'common': {
        'Farmer': {'min_coins': 50, 'max_coins': 100, 'min_xp': 2, 'max_xp': 8},
        'Fisher': {'min_coins': 40, 'max_coins': 90, 'min_xp': 2, 'max_xp': 7},
        'Merchant': {'min_coins': 60, 'max_coins': 120, 'min_xp': 3, 'max_xp': 10}
    },
    'uncommon': {
        'Guard': {'min_coins': 70, 'max_coins': 140, 'min_xp': 4, 'max_xp': 12},
        'Blacksmith': {'min_coins': 80, 'max_coins': 150, 'min_xp': 5, 'max_xp': 15},
        'Hunter': {'min_coins': 85, 'max_coins': 160, 'min_xp': 5, 'max_xp': 16}
    },
    'rare': {
        'Miner': {'min_coins': 90, 'max_coins': 180, 'min_xp': 6, 'max_xp': 18},
        'Alchemist': {'min_coins': 100, 'max_coins': 200, 'min_xp': 8, 'max_xp': 20},
        'Treasure Hunter': {'min_coins': 120, 'max_coins': 250, 'min_xp': 10, 'max_xp': 25}
    }
}

# AI Chat constants
AI_CONSTANTS = {
    'max_history_length': 20,
    'context_timeout_hours': 2,
    'conversation_timeout_minutes': 5,
    'max_response_length': 2000,
    'max_prompt_length': 500
}
