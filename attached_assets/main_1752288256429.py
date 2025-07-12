import discord
from discord.ext import commands
import os
import logging
import asyncio
from datetime import datetime
from keep_alive import keep_alive
from config import COLORS, EMOJIS, get_prefix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

# Create bot instance
bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    help_command=None,
    case_insensitive=True
)

@bot.event
async def on_ready():
    """Called when bot is ready."""
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    
    # Set bot activity
    activity = discord.Game(name="Epic RPG Adventure | $help")
    await bot.change_presence(activity=activity)
    
    # Load cogs
    await load_cogs()

async def load_cogs():
    """Load all cogs."""
    cog_files = [
        'cogs.rpg_games',
        'cogs.economy', 
        'cogs.moderation',
        'cogs.ai_chatbot',
        'cogs.admin'
    ]
    
    for cog in cog_files:
        try:
            await bot.load_extension(cog)
            logger.info(f'Loaded cog: {cog}')
        except Exception as e:
            logger.error(f'Failed to load cog {cog}: {e}')

@bot.event
async def on_command_error(ctx, error):
    """Global error handler."""
    if isinstance(error, commands.CommandNotFound):
        return
    
    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="⏰ Command on Cooldown",
            description=f"Please wait {error.retry_after:.1f} seconds before using this command again.",
            color=COLORS['warning']
        )
        await ctx.send(embed=embed, delete_after=10)
        
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Missing Permissions",
            description="You don't have permission to use this command.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed, delete_after=10)
        
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            title="❌ Bot Missing Permissions",
            description=f"I need the following permissions: {', '.join(error.missing_permissions)}",
            color=COLORS['error']
        )
        await ctx.send(embed=embed, delete_after=10)
        
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="❌ Member Not Found",
            description="Could not find that member.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed, delete_after=10)
        
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="❌ Invalid Argument",
            description="Please check your command arguments and try again.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed, delete_after=10)
        
    else:
        logger.error(f'Unhandled error in {ctx.command}: {error}')
        embed = discord.Embed(
            title="❌ An Error Occurred",
            description="Something went wrong while processing your command.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed, delete_after=10)

@bot.command(name='help')
async def help_command(ctx, *, command_name: str = None):
    """Custom help command."""
    if command_name:
        # Show help for specific command
        command = bot.get_command(command_name)
        if command:
            embed = discord.Embed(
                title=f"Help: {command.name}",
                description=command.help or "No description available.",
                color=COLORS['info']
            )
            if command.aliases:
                embed.add_field(
                    name="Aliases",
                    value=", ".join(command.aliases),
                    inline=False
                )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Command not found.")
        return
    
    # Show general help
    embed = discord.Embed(
        title="🎮 Epic RPG Helper - Commands",
        description="Here are all available commands:",
        color=COLORS['primary']
    )
    
    # RPG Commands
    rpg_commands = [
        "$start - Begin your RPG adventure",
        "$profile ($p) - View your character profile",
        "$adventure ($adv) - Go on an adventure",
        "$dungeon ($dg) - Enter a dangerous dungeon",
        "$heal - Restore your health",
        "$leaderboard ($lb) - View leaderboards"
    ]
    embed.add_field(
        name="🎯 RPG Commands",
        value="\n".join(rpg_commands),
        inline=False
    )
    
    # Economy Commands
    economy_commands = [
        "$work - Work to earn coins",
        "$daily - Claim daily reward",
        "$balance ($bal) - Check coin balance",
        "$shop - View the item shop",
        "$buy <item> - Buy an item",
        "$sell <item> - Sell an item",
        "$use <item> - Use an item",
        "$inventory ($inv) - View your inventory"
    ]
    embed.add_field(
        name="💰 Economy Commands",
        value="\n".join(economy_commands),
        inline=False
    )
    
    # Moderation Commands
    mod_commands = [
        "$kick <member> [reason] - Kick a member",
        "$ban <member> [reason] - Ban a member",
        "$unban <user_id> [reason] - Unban a user",
        "$mute <member> [duration] [reason] - Mute a member",
        "$unmute <member> [reason] - Unmute a member",
        "$clear <amount> - Clear messages",
        "$warn <member> [reason] - Warn a member",
        "$slowmode [seconds] - Set channel slowmode"
    ]
    embed.add_field(
        name="🔨 Moderation Commands",
        value="\n".join(mod_commands),
        inline=False
    )
    
    # AI Commands
    ai_commands = [
        "$chat <message> - Chat with AI",
        "$clear_chat - Clear AI conversation",
        "$ai_status - Check AI status"
    ]
    embed.add_field(
        name="🤖 AI Commands",
        value="\n".join(ai_commands),
        inline=False
    )
    
    # Admin Commands
    admin_commands = [
        "$toggle_module <module> - Toggle bot modules",
        "$set_prefix <prefix> - Set server prefix",
        "$bot_info - Show bot information",
        "$reload_cog <cog> - Reload a cog",
        "$ai_channel <add/remove> - Manage AI channels"
    ]
    embed.add_field(
        name="⚙️ Admin Commands",
        value="\n".join(admin_commands),
        inline=False
    )
    
    embed.set_footer(text="Use $help <command> for detailed information about a specific command")
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency."""
    start_time = datetime.now()
    message = await ctx.send("🏓 Pong!")
    end_time = datetime.now()
    
    api_latency = round(bot.latency * 1000)
    response_time = round((end_time - start_time).total_seconds() * 1000)
    
    embed = discord.Embed(
        title="🏓 Pong!",
        color=COLORS['success']
    )
    embed.add_field(name="API Latency", value=f"{api_latency}ms", inline=True)
    embed.add_field(name="Response Time", value=f"{response_time}ms", inline=True)
    
    await message.edit(content="", embed=embed)

def main():
    """Main function to run the bot."""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        return
    
    # Start keep-alive server
    keep_alive()
    
    # Run the bot
    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Invalid Discord token!")
    except Exception as e:
        logger.error(f"Error running bot: {e}")

if __name__ == "__main__":
    main()
