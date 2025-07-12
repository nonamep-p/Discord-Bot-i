import discord
import os
from typing import Dict, Any, List
from replit import db
import logging

logger = logging.getLogger(__name__)

# Color scheme
COLORS = {
    'primary': discord.Color.blue(),
    'secondary': discord.Color.purple(),
    'success': discord.Color.green(),
    'warning': discord.Color.orange(),
    'error': discord.Color.red(),
    'info': discord.Color.blurple()
}

# Emojis
EMOJIS = {
    'profile': '👤',
    'level': '📊',
    'xp': '⭐',
    'hp': '❤️',
    'attack': '⚔️',
    'defense': '🛡️',
    'coins': '💰',
    'inventory': '🎒',
    'skills': '🎯',
    'quest': '📜',
    'adventure': '🗺️',
    'dungeon': '🏰',
    'shop': '🏪',
    'work': '💼',
    'daily': '🎁'
}

# Default server configuration
DEFAULT_SERVER_CONFIG = {
    'prefix': '$',
    'modules': {
        'rpg_games': True,
        'economy': True,
        'moderation': True,
        'ai_chatbot': True,
        'admin': True
    },
    'ai_enabled_channels': [],
    'allowed_channels': [],
    'ai_custom_prompt': ''
}

def get_server_config(guild_id: int) -> Dict[str, Any]:
    """Get server configuration."""
    try:
        config_key = f"server_config_{guild_id}"
        
        if config_key in db:
            config = db[config_key]
            # Ensure all default keys exist
            for key, value in DEFAULT_SERVER_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
        else:
            # Create default config
            db[config_key] = DEFAULT_SERVER_CONFIG.copy()
            return DEFAULT_SERVER_CONFIG.copy()
    except Exception as e:
        logger.error(f"Error getting server config for {guild_id}: {e}")
        return DEFAULT_SERVER_CONFIG.copy()

def update_server_config(guild_id: int, updates: Dict[str, Any]):
    """Update server configuration."""
    try:
        config_key = f"server_config_{guild_id}"
        config = get_server_config(guild_id)
        config.update(updates)
        db[config_key] = config
    except Exception as e:
        logger.error(f"Error updating server config for {guild_id}: {e}")

def get_prefix(bot, message):
    """Get command prefix for guild."""
    if not message.guild:
        return '$'
    
    try:
        config = get_server_config(message.guild.id)
        return config.get('prefix', '$')
    except Exception as e:
        logger.error(f"Error getting prefix for guild {message.guild.id}: {e}")
        return '$'

def is_module_enabled(module_name: str, guild_id: int) -> bool:
    """Check if a module is enabled for a guild."""
    try:
        config = get_server_config(guild_id)
        return config.get('modules', {}).get(module_name, True)
    except Exception as e:
        logger.error(f"Error checking module {module_name} for guild {guild_id}: {e}")
        return True

def user_has_permission(member: discord.Member, permission: str) -> bool:
    """Check if user has required permission."""
    try:
        if member.guild_permissions.administrator:
            return True
        
        permission_map = {
            'manage_server': member.guild_permissions.manage_guild,
            'manage_messages': member.guild_permissions.manage_messages,
            'kick_members': member.guild_permissions.kick_members,
            'ban_members': member.guild_permissions.ban_members,
            'manage_roles': member.guild_permissions.manage_roles
        }
        
        return permission_map.get(permission, False)
    except Exception as e:
        logger.error(f"Error checking permissions for {member}: {e}")
        return False

def is_channel_allowed(channel_id: int, guild_id: int) -> bool:
    """Check if bot commands are allowed in channel."""
    try:
        config = get_server_config(guild_id)
        allowed_channels = config.get('allowed_channels', [])
        
        # If no channels specified, allow all
        if not allowed_channels:
            return True
        
        return channel_id in allowed_channels
    except Exception as e:
        logger.error(f"Error checking channel permissions for {channel_id}: {e}")
        return True

def is_ai_enabled_in_channel(channel_id: int, guild_id: int) -> bool:
    """Check if AI is enabled in specific channel."""
    try:
        config = get_server_config(guild_id)
        ai_channels = config.get('ai_enabled_channels', [])
        
        # If no channels specified, allow all
        if not ai_channels:
            return True
        
        return channel_id in ai_channels
    except Exception as e:
        logger.error(f"Error checking AI channel permissions for {channel_id}: {e}")
        return True

def add_ai_channel(channel_id: int, guild_id: int):
    """Add channel to AI enabled channels."""
    try:
        config = get_server_config(guild_id)
        ai_channels = config.get('ai_enabled_channels', [])
        
        if channel_id not in ai_channels:
            ai_channels.append(channel_id)
            update_server_config(guild_id, {'ai_enabled_channels': ai_channels})
    except Exception as e:
        logger.error(f"Error adding AI channel {channel_id} for guild {guild_id}: {e}")

def remove_ai_channel(channel_id: int, guild_id: int):
    """Remove channel from AI enabled channels."""
    try:
        config = get_server_config(guild_id)
        ai_channels = config.get('ai_enabled_channels', [])
        
        if channel_id in ai_channels:
            ai_channels.remove(channel_id)
            update_server_config(guild_id, {'ai_enabled_channels': ai_channels})
    except Exception as e:
        logger.error(f"Error removing AI channel {channel_id} for guild {guild_id}: {e}")

def toggle_module(module_name: str, guild_id: int) -> bool:
    """Toggle module on/off and return new state."""
    try:
        config = get_server_config(guild_id)
        modules = config.get('modules', {})
        
        current_state = modules.get(module_name, True)
        new_state = not current_state
        
        modules[module_name] = new_state
        update_server_config(guild_id, {'modules': modules})
        
        return new_state
    except Exception as e:
        logger.error(f"Error toggling module {module_name} for guild {guild_id}: {e}")
        return True

def set_custom_prefix(guild_id: int, prefix: str):
    """Set custom prefix for guild."""
    try:
        if len(prefix) > 5:
            raise ValueError("Prefix must be 5 characters or less")
        update_server_config(guild_id, {'prefix': prefix})
    except Exception as e:
        logger.error(f"Error setting prefix for guild {guild_id}: {e}")
        raise

def set_ai_custom_prompt(guild_id: int, prompt: str):
    """Set custom AI prompt for guild."""
    try:
        if len(prompt) > 500:
            raise ValueError("Prompt must be 500 characters or less")
        update_server_config(guild_id, {'ai_custom_prompt': prompt})
    except Exception as e:
        logger.error(f"Error setting AI prompt for guild {guild_id}: {e}")
        raise
