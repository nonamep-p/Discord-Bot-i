import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
from config import COLORS, EMOJIS, user_has_permission, is_module_enabled

class ModerationCog(commands.Cog):
    """Enhanced moderation commands with proper permissions."""
    
    def __init__(self, bot):
        self.bot = bot
        self.muted_users = {}  # Simple in-memory storage for muted users
        
    def can_moderate(self, ctx, target):
        """Check if user can moderate target."""
        if ctx.author == ctx.guild.owner:
            return True
            
        if target == ctx.guild.owner:
            return False
            
        if ctx.author.top_role <= target.top_role:
            return False
            
        return True
        
    @commands.command(name='kick', help='Kick a member from the server')
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick_member(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a member from the server."""
        if not is_module_enabled("moderation", ctx.guild.id):
            return
            
        if not self.can_moderate(ctx, member):
            embed = discord.Embed(
                title="❌ Insufficient Permissions",
                description="You cannot kick someone with a higher or equal role!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        if member.top_role >= ctx.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Bot Missing Permissions",
                description="I cannot kick someone with a higher or equal role than me!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        try:
            # Send DM to user before kicking
            try:
                dm_embed = discord.Embed(
                    title=f"Kicked from {ctx.guild.name}",
                    description=f"**Reason:** {reason}\n**Moderator:** {ctx.author}",
                    color=COLORS['error']
                )
                await member.send(embed=dm_embed)
            except:
                pass  # User might have DMs disabled
                
            await member.kick(reason=f"Kicked by {ctx.author} - {reason}")
            
            # Create log embed
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"**Member:** {member.mention} ({member})\n"
                           f"**Moderator:** {ctx.author.mention}\n"
                           f"**Reason:** {reason}",
                color=COLORS['warning']
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.timestamp = datetime.utcnow()
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to kick this member!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='ban', help='Ban a member from the server')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban_member(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Ban a member from the server."""
        if not is_module_enabled("moderation", ctx.guild.id):
            return
            
        if not self.can_moderate(ctx, member):
            embed = discord.Embed(
                title="❌ Insufficient Permissions",
                description="You cannot ban someone with a higher or equal role!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        if member.top_role >= ctx.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Bot Missing Permissions",
                description="I cannot ban someone with a higher or equal role than me!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        try:
            # Send DM to user before banning
            try:
                dm_embed = discord.Embed(
                    title=f"Banned from {ctx.guild.name}",
                    description=f"**Reason:** {reason}\n**Moderator:** {ctx.author}",
                    color=COLORS['error']
                )
                await member.send(embed=dm_embed)
            except:
                pass  # User might have DMs disabled
                
            await member.ban(reason=f"Banned by {ctx.author} - {reason}")
            
            # Create log embed
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**Member:** {member.mention} ({member})\n"
                           f"**Moderator:** {ctx.author.mention}\n"
                           f"**Reason:** {reason}",
                color=COLORS['error']
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.timestamp = datetime.utcnow()
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to ban this member!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='unban', help='Unban a user from the server')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban_member(self, ctx, user_id: int, *, reason="No reason provided"):
        """Unban a user from the server."""
        if not is_module_enabled("moderation", ctx.guild.id):
            return
            
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=f"Unbanned by {ctx.author} - {reason}")
            
            embed = discord.Embed(
                title="✅ Member Unbanned",
                description=f"**User:** {user.mention} ({user})\n"
                           f"**Moderator:** {ctx.author.mention}\n"
                           f"**Reason:** {reason}",
                color=COLORS['success']
            )
            embed.timestamp = datetime.utcnow()
            
            await ctx.send(embed=embed)
            
        except discord.NotFound:
            embed = discord.Embed(
                title="❌ User Not Found",
                description="User not found or not banned!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='mute', help='Mute a member')
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute_member(self, ctx, member: discord.Member, duration: int = 10, *, reason="No reason provided"):
        """Mute a member for a specified duration (in minutes)."""
        if not is_module_enabled("moderation", ctx.guild.id):
            return
            
        if not self.can_moderate(ctx, member):
            embed = discord.Embed(
                title="❌ Insufficient Permissions",
                description="You cannot mute someone with a higher or equal role!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        # Find or create muted role
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            try:
                muted_role = await ctx.guild.create_role(
                    name="Muted",
                    reason="Auto-created muted role",
                    permissions=discord.Permissions.none()
                )
                
                # Set permissions for muted role
                for channel in ctx.guild.channels:
                    if isinstance(channel, discord.TextChannel):
                        await channel.set_permissions(muted_role, send_messages=False, add_reactions=False)
                    elif isinstance(channel, discord.VoiceChannel):
                        await channel.set_permissions(muted_role, speak=False)
                        
            except discord.Forbidden:
                embed = discord.Embed(
                    title="❌ Permission Error",
                    description="I don't have permission to create the muted role!",
                    color=COLORS['error']
                )
                await ctx.send(embed=embed)
                return
                
        if muted_role in member.roles:
            embed = discord.Embed(
                title="❌ Already Muted",
                description="Member is already muted!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        try:
            await member.add_roles(muted_role, reason=f"Muted by {ctx.author} - {reason}")
            
            # Store mute info
            mute_end = datetime.utcnow() + timedelta(minutes=duration)
            self.muted_users[member.id] = {
                'guild_id': ctx.guild.id,
                'end_time': mute_end,
                'role': muted_role
            }
            
            # Create log embed
            embed = discord.Embed(
                title="🔇 Member Muted",
                description=f"**Member:** {member.mention} ({member})\n"
                           f"**Moderator:** {ctx.author.mention}\n"
                           f"**Duration:** {duration} minutes\n"
                           f"**Reason:** {reason}",
                color=COLORS['warning']
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.timestamp = datetime.utcnow()
            
            await ctx.send(embed=embed)
            
            # Schedule unmute
            await asyncio.sleep(duration * 60)
            if member.id in self.muted_users:
                try:
                    await member.remove_roles(muted_role, reason="Mute duration expired")
                    del self.muted_users[member.id]
                except:
                    pass
                    
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to mute this member!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='unmute', help='Unmute a member')
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute_member(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Unmute a member."""
        if not is_module_enabled("moderation", ctx.guild.id):
            return
            
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not muted_role or muted_role not in member.roles:
            embed = discord.Embed(
                title="❌ Not Muted",
                description="Member is not muted!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        try:
            await member.remove_roles(muted_role, reason=f"Unmuted by {ctx.author} - {reason}")
            
            # Remove from muted users tracking
            if member.id in self.muted_users:
                del self.muted_users[member.id]
            
            embed = discord.Embed(
                title="🔊 Member Unmuted",
                description=f"**Member:** {member.mention} ({member})\n"
                           f"**Moderator:** {ctx.author.mention}\n"
                           f"**Reason:** {reason}",
                color=COLORS['success']
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.timestamp = datetime.utcnow()
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to unmute this member!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='clear', aliases=['purge'], help='Clear messages')
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int = 10):
        """Clear messages from the channel."""
        if not is_module_enabled("moderation", ctx.guild.id):
            return
            
        if amount < 1 or amount > 100:
            embed = discord.Embed(
                title="❌ Invalid Amount",
                description="Please specify a number between 1 and 100.",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include the command message
            
            embed = discord.Embed(
                title="🧹 Messages Cleared",
                description=f"Deleted {len(deleted) - 1} messages.",
                color=COLORS['success']
            )
            
            # Send confirmation message that will auto-delete
            confirmation = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await confirmation.delete()
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to delete messages!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='slowmode', help='Set slowmode for the channel')
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        """Set slowmode for the channel."""
        if not is_module_enabled("moderation", ctx.guild.id):
            return
            
        if seconds < 0 or seconds > 21600:  # Max 6 hours
            embed = discord.Embed(
                title="❌ Invalid Duration",
                description="Slowmode must be between 0 and 21600 seconds (6 hours).",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        try:
            await ctx.channel.edit(slowmode_delay=seconds)
            
            if seconds == 0:
                embed = discord.Embed(
                    title="✅ Slowmode Disabled",
                    description="Slowmode has been disabled for this channel.",
                    color=COLORS['success']
                )
            else:
                embed = discord.Embed(
                    title="🐌 Slowmode Enabled",
                    description=f"Slowmode set to {seconds} seconds for this channel.",
                    color=COLORS['success']
                )
                
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to edit this channel!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            
    @commands.command(name='warn', help='Warn a member')
    @commands.has_permissions(manage_messages=True)
    async def warn_member(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Warn a member."""
        if not is_module_enabled("moderation", ctx.guild.id):
            return
            
        if not self.can_moderate(ctx, member):
            embed = discord.Embed(
                title="❌ Insufficient Permissions",
                description="You cannot warn someone with a higher or equal role!",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)
            return
            
        try:
            # Send DM to user
            try:
                dm_embed = discord.Embed(
                    title=f"Warning in {ctx.guild.name}",
                    description=f"**Reason:** {reason}\n**Moderator:** {ctx.author}",
                    color=COLORS['warning']
                )
                await member.send(embed=dm_embed)
            except:
                pass  # User might have DMs disabled
                
            # Create log embed
            embed = discord.Embed(
                title="⚠️ Member Warned",
                description=f"**Member:** {member.mention} ({member})\n"
                           f"**Moderator:** {ctx.author.mention}\n"
                           f"**Reason:** {reason}",
                color=COLORS['warning']
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.timestamp = datetime.utcnow()
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=COLORS['error']
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
