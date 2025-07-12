import logging
from replit import db
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def get_user_data(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user data from database."""
    try:
        if user_id in db:
            return db[user_id]
        return None
    except Exception as e:
        logger.error(f"Error getting user data for {user_id}: {e}")
        return None

def update_user_data(user_id: str, data: Dict[str, Any]) -> bool:
    """Update user data in database."""
    try:
        if user_id in db:
            db[user_id].update(data)
        else:
            db[user_id] = data
        return True
    except Exception as e:
        logger.error(f"Error updating user data for {user_id}: {e}")
        return False

def ensure_user_exists(user_id: str) -> bool:
    """Ensure user exists in database, create if not."""
    try:
        if user_id not in db:
            return False
        
        user_data = db[user_id]
        if 'rpg' not in user_data:
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error checking user existence for {user_id}: {e}")
        return False

def create_user_profile(user_id: str) -> Dict[str, Any]:
    """Create a new user profile."""
    try:
        profile_data = {
            'rpg': {
                'level': 1,
                'xp': 0,
                'max_xp': 100,
                'hp': 100,
                'max_hp': 100,
                'attack': 10,
                'defense': 5,
                'coins': 100,
                'inventory': [],
                'equipped': {
                    'weapon': None,
                    'armor': None
                },
                'last_adventure': None,
                'last_work': None,
                'last_daily': None,
                'adventure_count': 0,
                'dungeon_count': 0,
                'work_count': 0,
                'created_at': datetime.now().isoformat(),
                'stats': {
                    'total_adventures': 0,
                    'total_dungeons': 0,
                    'total_coins_earned': 0,
                    'total_xp_earned': 0,
                    'monsters_defeated': 0,
                    'items_found': 0
                }
            }
        }
        
        db[user_id] = profile_data
        return profile_data
    except Exception as e:
        logger.error(f"Error creating user profile for {user_id}: {e}")
        return {}

def get_user_rpg_data(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user's RPG data specifically."""
    try:
        user_data = get_user_data(user_id)
        if user_data and 'rpg' in user_data:
            return user_data['rpg']
        return None
    except Exception as e:
        logger.error(f"Error getting RPG data for {user_id}: {e}")
        return None

def update_user_rpg_data(user_id: str, rpg_data: Dict[str, Any]) -> bool:
    """Update user's RPG data specifically."""
    try:
        user_data = get_user_data(user_id)
        if user_data:
            user_data['rpg'] = rpg_data
            db[user_id] = user_data
            return True
        else:
            # Create new user data with RPG data
            db[user_id] = {'rpg': rpg_data}
            return True
    except Exception as e:
        logger.error(f"Error updating RPG data for {user_id}: {e}")
        return False

def get_leaderboard(stat: str, limit: int = 10) -> list:
    """Get leaderboard for a specific stat."""
    try:
        users = []
        for user_id, user_data in db.items():
            if (isinstance(user_data, dict) and 
                'rpg' in user_data and 
                not user_id.startswith('server_config_') and
                not user_id.startswith('backup_')):
                
                rpg_data = user_data['rpg']
                if stat in rpg_data:
                    users.append({
                        'user_id': user_id,
                        'value': rpg_data[stat],
                        'level': rpg_data.get('level', 1)
                    })
        
        # Sort by the stat value in descending order
        users.sort(key=lambda x: x['value'], reverse=True)
        return users[:limit]
    except Exception as e:
        logger.error(f"Error getting leaderboard for {stat}: {e}")
        return []

def backup_user_data(user_id: str) -> bool:
    """Create a backup of user data."""
    try:
        user_data = get_user_data(user_id)
        if user_data:
            backup_key = f"backup_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            db[backup_key] = user_data
            return True
        return False
    except Exception as e:
        logger.error(f"Error backing up user data for {user_id}: {e}")
        return False

def cleanup_old_backups(days_old: int = 30) -> int:
    """Clean up old backup data."""
    try:
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        keys_to_delete = []
        for key in db.keys():
            if key.startswith('backup_'):
                try:
                    # Extract timestamp from backup key
                    timestamp_str = key.split('_')[-2] + '_' + key.split('_')[-1]
                    backup_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    if backup_date < cutoff_date:
                        keys_to_delete.append(key)
                except:
                    continue
        
        for key in keys_to_delete:
            del db[key]
        
        return len(keys_to_delete)
    except Exception as e:
        logger.error(f"Error cleaning up old backups: {e}")
        return 0

def get_database_stats() -> Dict[str, Any]:
    """Get database statistics."""
    try:
        stats = {
            'total_keys': 0,
            'user_profiles': 0,
            'server_configs': 0,
            'backups': 0,
            'other_keys': 0
        }
        
        for key in db.keys():
            stats['total_keys'] += 1
            
            if key.startswith('server_config_'):
                stats['server_configs'] += 1
            elif key.startswith('backup_'):
                stats['backups'] += 1
            elif isinstance(db[key], dict) and 'rpg' in db[key]:
                stats['user_profiles'] += 1
            else:
                stats['other_keys'] += 1
                
        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {}
