import discord
from discord.ext import commands
import os
import psutil
from datetime import datetime
from config import (
    COLORS, EMOJIS, user_has_permission, is_module_enabled, 
    toggle_module, set_custom_prefix, get_server_config, 
    add_ai_channel, remove_ai_channel, set_ai_custom_prompt
)
from utils.helpers import create_embed, format_number
from utils.database import get_database_stats, cleanup_old_backups
import logging

logger = logging.getLogger(__name__)

class AdminCog(commands.Cog):
    """Admin commands for bot management."""
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='toggle_module', help='Toggle bot modules on/off')
    @commands.has_permissions(manage_guild=True)
    async def toggle_module_command(self, ctx, module_name: str):
        """Toggle a bot module on or off."""
        valid_modules = ['rpg_games', 'economy', 'moderation', 'ai_chatbot', 'admin']
        
        if module_name not in valid_modules:
            embed = discord.Embed(
                title="❌ Invalid Module",
                description=f"Valid modules: {', '.join(valid_modules)}",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        if module_name == 'admin':
            embed = discord.Embed(
                title="❌ Cannot Toggle Admin",
                description="The admin module cannot be disabled.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        try:
            new_state = toggle_module(module_name, ctx.guild.id)
            
            status = "enabled" if new_state else "disabled"
            color = COLORS['success'] if new_state else COLORS['warning']
            
            embed = discord.Embed(
                title=f"🔧 Module {status.title()}",
                description=f"The **{module_name}** module has been {status}.",
                color=color
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error toggling module {module_name}: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while toggling the module.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='set_prefix', help='Set custom prefix for this server')
    @commands.has_permissions(manage_guild=True)
    async def set_prefix_command(self, ctx, prefix: str):
        """Set a custom prefix for the server."""
        if len(prefix) > 5:
            embed = discord.Embed(
                title="❌ Invalid Prefix",
                description="Prefix must be 5 characters or less.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        try:
            set_custom_prefix(ctx.guild.id, prefix)
            
            embed = discord.Embed(
                title="✅ Prefix Updated",
                description=f"Server prefix has been changed to `{prefix}`",
                color=COLORS['success']
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error setting prefix: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while setting the prefix.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='info', help='Show bot information')
    async def bot_info(self, ctx):
        """Display bot information."""
        embed = discord.Embed(
            title="🤖 Epic RPG Helper - Bot Information",
            color=COLORS['info']
        )
        
        # Bot stats
        guild_count = len(self.bot.guilds)
        user_count = len(set(self.bot.get_all_members()))
        
        embed.add_field(
            name="📊 Bot Stats",
            value=f"**Servers:** {guild_count}\n"
                  f"**Users:** {format_number(user_count)}\n"
                  f"**Latency:** {round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        # System info
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            embed.add_field(
                name="🖥️ System Info",
                value=f"**CPU Usage:** {cpu_percent}%\n"
                      f"**Memory Usage:** {memory.percent}%\n"
                      f"**Memory Available:** {memory.available // 1024 // 1024}MB",
                inline=True
            )
        except:
            embed.add_field(
                name="🖥️ System Info",
                value="System info unavailable",
                inline=True
            )
        
        # Database stats
        try:
            db_stats = get_database_stats()
            embed.add_field(
                name="💾 Database Stats",
                value=f"**Total Keys:** {db_stats.get('total_keys', 0)}\n"
                      f"**User Profiles:** {db_stats.get('user_profiles', 0)}\n"
                      f"**Server Configs:** {db_stats.get('server_configs', 0)}",
                inline=True
            )
        except:
            embed.add_field(
                name="💾 Database Stats",
                value="Database stats unavailable",
                inline=True
            )
        
        # Features
        embed.add_field(
            name="🎮 Features",
            value="• RPG Adventure System\n"
                  "• Economy & Shop\n"
                  "• Moderation Tools\n"
                  "• AI Chatbot\n"
                  "• Interactive UI",
            inline=True
        )
        
        # Version info
        embed.add_field(
            name="📦 Version Info",
            value=f"**Bot Version:** 2.0.0\n"
                  f"**Discord.py:** {discord.__version__}\n"
                  f"**Python:** {psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}",
            inline=True
        )
        
        embed.set_footer(text="Epic RPG Helper - Created with ❤️")
        await ctx.send(embed=embed)
        
    @commands.command(name='server_config', help='Show server configuration')
    @commands.has_permissions(manage_guild=True)
    async def server_config(self, ctx):
        """Display server configuration."""
        try:
            config = get_server_config(ctx.guild.id)
            
            embed = discord.Embed(
                title=f"⚙️ {ctx.guild.name} Configuration",
                color=COLORS['info']
            )
            
            # Basic settings
            embed.add_field(
                name="📝 Basic Settings",
                value=f"**Prefix:** `{config.get('prefix', '$')}`\n"
                      f"**AI Custom Prompt:** {'Set' if config.get('ai_custom_prompt') else 'Default'}",
                inline=False
            )
            
            # Module status
            modules = config.get('modules', {})
            module_status = []
            for module, enabled in modules.items():
                status = "✅" if enabled else "❌"
                module_status.append(f"{status} {module}")
                
            embed.add_field(
                name="🔧 Module Status",
                value="\n".join(module_status),
                inline=False
            )
            
            # AI channels
            ai_channels = config.get('ai_enabled_channels', [])
            if ai_channels:
                channel_mentions = []
                for channel_id in ai_channels:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        channel_mentions.append(channel.mention)
                        
                embed.add_field(
                    name="🤖 AI Enabled Channels",
                    value="\n".join(channel_mentions) if channel_mentions else "None",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🤖 AI Enabled Channels",
                    value="All channels (default)",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error displaying server config: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while retrieving server configuration.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='ai_channel', help='Manage AI enabled channels')
    @commands.has_permissions(manage_guild=True)
    async def ai_channel_command(self, ctx, action: str, channel: discord.TextChannel = None):
        """Add or remove AI enabled channels."""
        if not is_module_enabled("ai_chatbot", ctx.guild.id):
            embed = discord.Embed(
                title="❌ AI Module Disabled",
                description="The AI chatbot module is disabled. Enable it with `$toggle_module ai_chatbot`",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        if action.lower() not in ['add', 'remove']:
            embed = discord.Embed(
                title="❌ Invalid Action",
                description="Use `add` or `remove` to manage AI channels.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        if not channel:
            channel = ctx.channel
            
        try:
            if action.lower() == 'add':
                add_ai_channel(channel.id, ctx.guild.id)
                embed = discord.Embed(
                    title="✅ AI Channel Added",
                    description=f"AI chatbot enabled in {channel.mention}",
                    color=COLORS['success']
                )
            else:
                remove_ai_channel(channel.id, ctx.guild.id)
                embed = discord.Embed(
                    title="✅ AI Channel Removed",
                    description=f"AI chatbot disabled in {channel.mention}",
                    color=COLORS['success']
                )
                
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error managing AI channel: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while managing AI channels.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='set_ai_prompt', help='Set custom AI prompt for this server')
    @commands.has_permissions(manage_guild=True)
    async def set_ai_prompt_command(self, ctx, *, prompt: str):
        """Set a custom AI prompt for the server."""
        if not is_module_enabled("ai_chatbot", ctx.guild.id):
            embed = discord.Embed(
                title="❌ AI Module Disabled",
                description="The AI chatbot module is disabled. Enable it with `$toggle_module ai_chatbot`",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        if len(prompt) > 500:
            embed = discord.Embed(
                title="❌ Prompt Too Long",
                description="AI prompt must be 500 characters or less.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        try:
            set_ai_custom_prompt(ctx.guild.id, prompt)
            
            embed = discord.Embed(
                title="✅ AI Prompt Updated",
                description=f"Custom AI prompt has been set for this server.",
                color=COLORS['success']
            )
            embed.add_field(
                name="Custom Prompt",
                value=f"```{prompt}```",
                inline=False
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error setting AI prompt: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while setting the AI prompt.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='reset_ai_prompt', help='Reset AI prompt to default')
    @commands.has_permissions(manage_guild=True)
    async def reset_ai_prompt_command(self, ctx):
        """Reset AI prompt to default."""
        if not is_module_enabled("ai_chatbot", ctx.guild.id):
            embed = discord.Embed(
                title="❌ AI Module Disabled",
                description="The AI chatbot module is disabled. Enable it with `$toggle_module ai_chatbot`",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        try:
            set_ai_custom_prompt(ctx.guild.id, "")
            
            embed = discord.Embed(
                title="✅ AI Prompt Reset",
                description="AI prompt has been reset to default.",
                color=COLORS['success']
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error resetting AI prompt: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while resetting the AI prompt.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='cleanup_database', help='Clean up old database entries')
    @commands.has_permissions(administrator=True)
    async def cleanup_database_command(self, ctx, days: int = 30):
        """Clean up old database entries."""
        if days < 1 or days > 365:
            embed = discord.Embed(
                title="❌ Invalid Days",
                description="Days must be between 1 and 365.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        try:
            # Show confirmation
            embed = discord.Embed(
                title="⚠️ Database Cleanup",
                description=f"This will delete backup data older than {days} days.\n"
                           f"Are you sure you want to continue?",
                color=COLORS['warning']
            )
            
            confirm_msg = await ctx.send(embed=embed)
            await confirm_msg.add_reaction("✅")
            await confirm_msg.add_reaction("❌")
            
            def check(reaction, user):
                return user == ctx.author and reaction.message.id == confirm_msg.id and str(reaction.emoji) in ["✅", "❌"]
            
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
                
                if str(reaction.emoji) == "✅":
                    deleted_count = cleanup_old_backups(days)
                    
                    embed = discord.Embed(
                        title="✅ Database Cleanup Complete",
                        description=f"Deleted {deleted_count} old backup entries.",
                        color=COLORS['success']
                    )
                    await confirm_msg.edit(embed=embed)
                else:
                    embed = discord.Embed(
                        title="❌ Database Cleanup Cancelled",
                        description="Database cleanup was cancelled.",
                        color=COLORS['error']
                    )
                    await confirm_msg.edit(embed=embed)
                    
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    title="⏰ Database Cleanup Timeout",
                    description="Database cleanup was cancelled due to timeout.",
                    color=COLORS['warning']
                )
                await confirm_msg.edit(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in database cleanup: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred during database cleanup.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='reload_cog', help='Reload a bot cog')
    @commands.has_permissions(administrator=True)
    async def reload_cog_command(self, ctx, cog_name: str):
        """Reload a specific cog."""
        valid_cogs = ['rpg_games', 'economy', 'moderation', 'ai_chatbot', 'admin']
        
        if cog_name not in valid_cogs:
            embed = discord.Embed(
                title="❌ Invalid Cog",
                description=f"Valid cogs: {', '.join(valid_cogs)}",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        try:
            cog_path = f'cogs.{cog_name}'
            await self.bot.reload_extension(cog_path)
            
            embed = discord.Embed(
                title="✅ Cog Reloaded",
                description=f"Successfully reloaded the **{cog_name}** cog.",
                color=COLORS['success']
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error reloading cog {cog_name}: {e}")
            embed = discord.Embed(
                title="❌ Reload Failed",
                description=f"Failed to reload the **{cog_name}** cog.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='eval', help='Evaluate Python code')
    @commands.has_permissions(administrator=True)
    async def eval_command(self, ctx, *, code: str):
        """Evaluate Python code. Admin only."""
        if ctx.author.id != 123456789:  # Replace with your Discord ID
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="This command is restricted to the bot owner.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        try:
            # Remove code blocks if present
            if code.startswith('```py'):
                code = code[5:-3]
            elif code.startswith('```'):
                code = code[3:-3]
                
            # Execute code
            result = eval(code)
            
            embed = discord.Embed(
                title="✅ Code Executed",
                description=f"```py\n{code}\n```",
                color=COLORS['success']
            )
            embed.add_field(
                name="Result",
                value=f"```py\n{result}\n```",
                inline=False
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Execution Error",
                description=f"```py\n{code}\n```",
                color=COLORS['error']
            )
            embed.add_field(
                name="Error",
                value=f"```py\n{str(e)}\n```",
                inline=False
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
