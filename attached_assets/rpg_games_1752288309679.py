import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime, timedelta
from replit import db
from config import COLORS, EMOJIS, is_module_enabled
from utils.database import get_user_data, update_user_data, ensure_user_exists, create_user_profile, get_user_rpg_data, update_user_rpg_data
from utils.helpers import create_embed, format_number, create_progress_bar, level_up_player, get_random_adventure_outcome, get_time_until_next_use, format_time_remaining
from utils.rng_system import roll_with_luck, check_rare_event, get_luck_status
from utils.constants import RPG_CONSTANTS, MONSTERS, ADVENTURE_LOCATIONS, DUNGEON_TYPES
import logging

logger = logging.getLogger(__name__)

class RPGProfileView(discord.ui.View):
    """Interactive view for RPG profile."""

    def __init__(self, user, player_data):
        super().__init__(timeout=300)
        self.user = user
        self.player_data = player_data
        self.current_page = "stats"

    @discord.ui.button(label="📊 Stats", style=discord.ButtonStyle.primary)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show player stats."""
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your profile!", ephemeral=True)
            return

        self.current_page = "stats"
        embed = self.create_stats_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🎒 Inventory", style=discord.ButtonStyle.secondary)
    async def inventory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show player inventory."""
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your profile!", ephemeral=True)
            return

        self.current_page = "inventory"
        embed = self.create_inventory_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🎯 Skills", style=discord.ButtonStyle.success)
    async def skills_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show player skills."""
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your profile!", ephemeral=True)
            return

        self.current_page = "skills"
        embed = self.create_skills_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🏆 Achievements", style=discord.ButtonStyle.danger)
    async def achievements_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show player achievements."""
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your profile!", ephemeral=True)
            return

        self.current_page = "achievements"
        embed = self.create_achievements_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🍀 Luck", style=discord.ButtonStyle.success)
    async def luck_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show player luck status."""
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your profile!", ephemeral=True)
            return

        self.current_page = "luck"
        embed = self.create_luck_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def create_stats_embed(self):
        """Create stats embed."""
        try:
            xp_progress = (self.player_data['xp'] / self.player_data['max_xp']) * 100
            progress_bar = create_progress_bar(xp_progress)

            embed = discord.Embed(
                title=f"{EMOJIS['profile']} {self.user.display_name}'s Profile",
                description=f"**Level {self.player_data['level']} Adventurer**",
                color=COLORS['primary']
            )
            embed.set_thumbnail(url=self.user.display_avatar.url)

            # Core Stats
            embed.add_field(
                name="📊 Core Stats",
                value=f"**{EMOJIS['level']} Level:** {self.player_data['level']}\n"
                      f"**{EMOJIS['xp']} XP:** {self.player_data['xp']}/{self.player_data['max_xp']}\n"
                      f"{progress_bar}\n"
                      f"**{EMOJIS['hp']} HP:** {self.player_data['hp']}/{self.player_data['max_hp']}\n"
                      f"**{EMOJIS['attack']} Attack:** {self.player_data['attack']}\n"
                      f"**{EMOJIS['defense']} Defense:** {self.player_data['defense']}",
                inline=True
            )

            # Economy & Progress
            embed.add_field(
                name="💰 Economy & Progress",
                value=f"**{EMOJIS['coins']} Coins:** {format_number(self.player_data['coins'])}\n"
                      f"**🎯 Adventures:** {self.player_data.get('adventure_count', 0)}\n"
                      f"**🏰 Dungeons:** {self.player_data.get('dungeon_count', 0)}\n"
                      f"**🎒 Items:** {len(self.player_data.get('inventory', []))}",
                inline=True
            )

            # Equipment
            weapon = self.player_data.get('equipped', {}).get('weapon', 'None')
            armor = self.player_data.get('equipped', {}).get('armor', 'None')
            embed.add_field(
                name="🎯 Equipment",
                value=f"**⚔️ Weapon:** {weapon}\n**🛡️ Armor:** {armor}",
                inline=True
            )

            embed.set_footer(text="Use the buttons below to navigate different sections")
            return embed
        except Exception as e:
            logger.error(f"Error creating stats embed: {e}")
            return create_embed("Error", "Failed to create stats embed.", COLORS['error'])

    def create_inventory_embed(self):
        """Create inventory embed."""
        try:
            embed = discord.Embed(
                title=f"{EMOJIS['inventory']} {self.user.display_name}'s Inventory",
                color=COLORS['secondary']
            )
            embed.set_thumbnail(url=self.user.display_avatar.url)

            inventory = self.player_data.get('inventory', [])

            if not inventory:
                embed.description = "Your inventory is empty! Go on adventures to find items."
            else:
                # Group items by type
                item_groups = {}
                for item in inventory:
                    item_type = self.get_item_type(item)
                    if item_type not in item_groups:
                        item_groups[item_type] = []
                    item_groups[item_type].append(item)

                # Display grouped items
                for item_type, items in item_groups.items():
                    item_counts = {}
                    for item in items:
                        item_counts[item] = item_counts.get(item, 0) + 1

                    item_list = []
                    for item, count in item_counts.items():
                        if count > 1:
                            item_list.append(f"{item} x{count}")
                        else:
                            item_list.append(item)

                    embed.add_field(
                        name=f"{self.get_item_emoji(item_type)} {item_type.title()}",
                        value="\n".join(item_list) if item_list else "None",
                        inline=True
                    )

            embed.set_footer(text="Use $use <item> to use items from your inventory")
            return embed
        except Exception as e:
            logger.error(f"Error creating inventory embed: {e}")
            return create_embed("Error", "Failed to create inventory embed.", COLORS['error'])

    def create_skills_embed(self):
        """Create skills embed."""
        try:
            embed = discord.Embed(
                title=f"{EMOJIS['skills']} {self.user.display_name}'s Skills",
                color=COLORS['info']
            )
            embed.set_thumbnail(url=self.user.display_avatar.url)

            level = self.player_data['level']

            # Calculate skill levels based on player level and activities
            combat_skill = min(level + self.player_data.get('dungeon_count', 0) // 5, 100)
            exploration_skill = min(level + self.player_data.get('adventure_count', 0) // 10, 100)
            trading_skill = min(level + (self.player_data.get('coins', 0) // 1000), 100)

            embed.add_field(
                name="⚔️ Combat",
                value=f"Level {combat_skill}\n{create_progress_bar(combat_skill)}",
                inline=True
            )

            embed.add_field(
                name="🗺️ Exploration",
                value=f"Level {exploration_skill}\n{create_progress_bar(exploration_skill)}",
                inline=True
            )

            embed.add_field(
                name="💰 Trading",
                value=f"Level {trading_skill}\n{create_progress_bar(trading_skill)}",
                inline=True
            )

            embed.set_footer(text="Skills improve as you play and gain experience")
            return embed
        except Exception as e:
            logger.error(f"Error creating skills embed: {e}")
            return create_embed("Error", "Failed to create skills embed.", COLORS['error'])

    def create_achievements_embed(self):
        """Create achievements embed."""
        try:
            embed = discord.Embed(
                title=f"🏆 {self.user.display_name}'s Achievements",
                color=COLORS['warning']
            )
            embed.set_thumbnail(url=self.user.display_avatar.url)

            # Sample achievements based on player stats
            achievements = []
            
            if self.player_data.get('adventure_count', 0) >= 1:
                achievements.append("🎯 First Steps - Complete your first adventure")
            
            if self.player_data.get('adventure_count', 0) >= 10:
                achievements.append("🗺️ Explorer - Complete 10 adventures")
                
            if self.player_data.get('dungeon_count', 0) >= 1:
                achievements.append("🏰 Dungeon Delver - Complete your first dungeon")
                
            if self.player_data.get('level', 1) >= 10:
                achievements.append("⭐ Experienced - Reach level 10")
                
            if self.player_data.get('coins', 0) >= 1000:
                achievements.append("💰 Wealthy - Accumulate 1,000 coins")

            if achievements:
                embed.description = "\n".join(achievements)
            else:
                embed.description = "No achievements yet. Start your adventure to unlock them!"

            embed.set_footer(text="Complete more activities to unlock achievements!")
            return embed
        except Exception as e:
            logger.error(f"Error creating achievements embed: {e}")
            return create_embed("Error", "Failed to create achievements embed.", COLORS['error'])

    def create_luck_embed(self):
        """Create luck status embed."""
        try:
            luck_status = get_luck_status(self.user.id)
            
            embed = discord.Embed(
                title=f"🍀 {self.user.display_name}'s Luck Status",
                color=COLORS['info']
            )
            
            # Luck tier with emoji
            luck_emojis = {
                "cursed": "💀",
                "unlucky": "😰",
                "normal": "😐",
                "lucky": "😊",
                "blessed": "✨",
                "divine": "🌟"
            }
            
            luck_emoji = luck_emojis.get(luck_status['luck_tier'], "🍀")
            
            embed.add_field(
                name="🎲 Current Luck",
                value=f"{luck_emoji} **{luck_status['luck_tier'].title()}**\n"
                      f"Multiplier: {luck_status['luck_multiplier']:.2f}x\n"
                      f"Lucky Streak: {luck_status['lucky_streak']}",
                inline=True
            )
            
            # Active conditions
            if luck_status['active_conditions']:
                embed.add_field(
                    name="⚡ Active Conditions",
                    value="\n".join(luck_status['active_conditions']),
                    inline=False
                )
            else:
                embed.add_field(
                    name="⚡ Active Conditions",
                    value="None active",
                    inline=False
                )
            
            # Rare events found
            if luck_status['rare_events_found']:
                rare_events_text = "\n".join([f"• {event.replace('_', ' ').title()}" for event in luck_status['rare_events_found']])
                embed.add_field(
                    name="✨ Rare Events Discovered",
                    value=rare_events_text,
                    inline=False
                )
            else:
                embed.add_field(
                    name="✨ Rare Events Discovered",
                    value="None yet - keep exploring!",
                    inline=False
                )
            
            embed.add_field(
                name="📊 Statistics",
                value=f"Total Rare Events: {luck_status['total_rare_events']}\n"
                      f"Luck Tier: {luck_status['luck_tier'].title()}",
                inline=True
            )
            
            embed.set_footer(text="Luck affects all your adventures and activities!")
            
            return embed
            
        except Exception as e:
            logger.error(f"Error creating luck embed: {e}")
            return discord.Embed(
                title="❌ Error",
                description="Could not load luck status.",
                color=COLORS['error']
            )

    def get_item_type(self, item):
        """Get item type from item name."""
        item_lower = item.lower()
        if any(weapon in item_lower for weapon in ['sword', 'blade', 'dagger', 'axe', 'bow']):
            return 'weapons'
        elif any(armor in item_lower for armor in ['armor', 'shield', 'helmet', 'mail']):
            return 'armor'
        elif any(consumable in item_lower for consumable in ['potion', 'elixir', 'scroll']):
            return 'consumables'
        else:
            return 'misc'

    def get_item_emoji(self, item_type):
        """Get emoji for item type."""
        emojis = {
            'weapons': '⚔️',
            'armor': '🛡️',
            'consumables': '🧪',
            'misc': '📦'
        }
        return emojis.get(item_type, '📦')

class RPGGamesCog(commands.Cog):
    """RPG Games system with interactive UI."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='start', help='Begin your RPG adventure!')
    async def start_adventure(self, ctx):
        """Create a new player profile."""
        if not is_module_enabled("rpg_games", ctx.guild.id):
            return
            
        user_id = str(ctx.author.id)

        if ensure_user_exists(user_id):
            embed = discord.Embed(
                title="🎮 Adventure Already Started!",
                description=f"{ctx.author.mention}, you've already begun your adventure!\nUse `{ctx.prefix}profile` to see your stats.",
                color=COLORS['warning']
            )
            await ctx.send(embed=embed)
            return

        # Create new player profile
        try:
            create_user_profile(user_id)

            embed = discord.Embed(
                title="🎮 Adventure Begins!",
                description=f"Welcome, {ctx.author.mention}! Your epic RPG adventure starts now!",
                color=COLORS['success']
            )
            embed.add_field(
                name="Starting Stats",
                value=f"**Level:** 1\n**HP:** 100/100\n**Attack:** 10\n**Defense:** 5\n**Coins:** 💰 100",
                inline=True
            )
            embed.add_field(
                name="Next Steps",
                value=f"Use `{ctx.prefix}profile` to see your full stats\nUse `{ctx.prefix}adventure` to start exploring!",
                inline=True
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            embed.set_footer(text="Your adventure awaits!")

            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error creating profile for {user_id}: {e}")
            await ctx.send("❌ An error occurred while creating your profile. Please try again.")

    @commands.command(name='profile', aliases=['p'], help='View your interactive player profile')
    async def view_profile(self, ctx, member: discord.Member = None):
        """Display interactive player profile."""
        if not is_module_enabled("rpg_games", ctx.guild.id):
            return
            
        target = member or ctx.author
        user_id = str(target.id)

        if not ensure_user_exists(user_id):
            if target == ctx.author:
                embed = discord.Embed(
                    title="No Adventure Started",
                    description=f"You haven't started your adventure yet! Use `{ctx.prefix}start` to begin.",
                    color=COLORS['error']
                )
            else:
                embed = discord.Embed(
                    title="No Adventure Started",
                    description=f"{target.mention} hasn't started their adventure yet!",
                    color=COLORS['error']
                )
            await ctx.send(embed=embed)
            return

        try:
            player_data = get_user_rpg_data(user_id)
            
            if not player_data:
                await ctx.send("❌ Error retrieving player data. Please try again.")
                return
            
            # Create interactive view
            view = RPGProfileView(target, player_data)
            embed = view.create_stats_embed()
            
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            logger.error(f"Error displaying profile for {user_id}: {e}")
            await ctx.send("❌ An error occurred while displaying the profile. Please try again.")

    @commands.command(name='luck', help='Check your luck status and discover hidden conditions!')
    async def luck_status(self, ctx):
        """Check player's luck status."""
        if not is_module_enabled("rpg_games", ctx.guild.id):
            return
            
        user_id = str(ctx.author.id)
        
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to `$start` your adventure first!")
            return
            
        try:
            luck_status = get_luck_status(ctx.author.id)
            
            embed = discord.Embed(
                title=f"🍀 {ctx.author.display_name}'s Luck Status",
                color=COLORS['info']
            )
            
            # Luck tier with emoji
            luck_emojis = {
                "cursed": "💀",
                "unlucky": "😰",
                "normal": "😐",
                "lucky": "😊",
                "blessed": "✨",
                "divine": "🌟"
            }
            
            luck_emoji = luck_emojis.get(luck_status['luck_tier'], "🍀")
            
            embed.add_field(
                name="🎲 Current Luck",
                value=f"{luck_emoji} **{luck_status['luck_tier'].title()}**\n"
                      f"Multiplier: {luck_status['luck_multiplier']:.2f}x\n"
                      f"Lucky Streak: {luck_status['lucky_streak']}",
                inline=True
            )
            
            # Active conditions
            if luck_status['active_conditions']:
                embed.add_field(
                    name="⚡ Active Conditions",
                    value="\n".join(luck_status['active_conditions']),
                    inline=False
                )
            else:
                embed.add_field(
                    name="⚡ Active Conditions",
                    value="None active - some conditions are hidden and appear randomly!",
                    inline=False
                )
            
            # Rare events found
            if luck_status['rare_events_found']:
                rare_events_text = "\n".join([f"• {event.replace('_', ' ').title()}" for event in luck_status['rare_events_found']])
                embed.add_field(
                    name="✨ Rare Events Discovered",
                    value=rare_events_text,
                    inline=False
                )
            else:
                embed.add_field(
                    name="✨ Rare Events Discovered",
                    value="None yet - keep exploring to find legendary events!",
                    inline=False
                )
            
            embed.add_field(
                name="📊 Statistics",
                value=f"Total Rare Events: {luck_status['total_rare_events']}\n"
                      f"Luck Tier: {luck_status['luck_tier'].title()}",
                inline=True
            )
            
            embed.add_field(
                name="🔮 Hidden Conditions",
                value="Some luck conditions are secret and activate based on:\n"
                      "• Time of day\n"
                      "• Your user ID digits\n"
                      "• Random celestial events\n"
                      "• Your activity patterns",
                inline=False
            )
            
            embed.set_footer(text="Luck affects all your adventures and activities! Some conditions are hidden until discovered.")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error displaying luck status: {e}")
            await ctx.send("❌ An error occurred while checking your luck status.")

    @commands.command(name='adventure', aliases=['adv'], help='Go on an adventure!')
    @commands.cooldown(1, RPG_CONSTANTS['adventure_cooldown'], commands.BucketType.user)
    async def adventure(self, ctx):
        """Adventure command with various outcomes."""
        if not is_module_enabled("rpg_games", ctx.guild.id):
            return
            
        user_id = str(ctx.author.id)
        
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to `$start` your adventure first!")
            return
            
        try:
            player_data = get_user_rpg_data(user_id)
            
            if not player_data:
                await ctx.send("❌ Error retrieving player data. Please try again.")
                return
            
            if player_data['hp'] <= 0:
                await ctx.send("❌ You need to heal before going on adventures! Use `$heal` to restore your health.")
                return
                
            # Check for rare events first
            rare_event = check_rare_event(int(user_id))
            
            # Get random adventure outcome
            outcome = get_random_adventure_outcome()
            location = random.choice(ADVENTURE_LOCATIONS)
            
            coins_gained = random.randint(outcome['min_coins'], outcome['max_coins'])
            xp_gained = random.randint(outcome['min_xp'], outcome['max_xp'])
            items_found = []
            damage_taken = 0
            
            # Apply luck to success rates
            success_roll, luck_info = roll_with_luck(int(user_id), 0.7, "adventure")
            
            # Level bonus
            level_bonus = int(coins_gained * 0.1 * player_data['level'])
            coins_gained += level_bonus
            
            # Luck bonus
            if success_roll:
                luck_bonus = int(coins_gained * 0.2)
                coins_gained += luck_bonus
                xp_gained = int(xp_gained * 1.1)
            
            # Process different outcome types
            if outcome['type'] == 'monster':
                # Combat simulation
                monster = random.choice(MONSTERS['common'])
                player_damage = player_data['attack'] + random.randint(1, 10)
                monster_damage = monster['attack'] - player_data['defense']
                monster_damage = max(1, monster_damage + random.randint(-2, 2))
                
                if player_damage >= monster['hp']:
                    description = f"⚔️ In the {location}, you encountered a {monster['name']} and defeated it!\n"
                    description += f"💰 Gained {format_number(coins_gained)} coins and {xp_gained} XP!"
                else:
                    damage_taken = random.randint(monster_damage//2, monster_damage)
                    player_data['hp'] = max(1, player_data['hp'] - damage_taken)
                    description = f"⚔️ In the {location}, you fought a {monster['name']} but took {damage_taken} damage!\n"
                    description += f"💰 Still gained {format_number(coins_gained)} coins and {xp_gained} XP."
                    
            elif outcome['type'] == 'treasure':
                description = f"💰 In the {location}, you discovered a hidden treasure chest!\n"
                description += f"💰 Gained {format_number(coins_gained)} coins and {xp_gained} XP!"
                
            elif outcome['type'] == 'rare_find':
                rare_items = ['Ancient Coin', 'Magic Crystal', 'Enchanted Gem', 'Rare Herb', 'Mystical Orb']
                found_item = random.choice(rare_items)
                items_found.append(found_item)
                description = f"✨ In the {location}, you made a rare discovery!\n"
                description += f"🎒 Found: {found_item}\n"
                description += f"💰 Gained {format_number(coins_gained)} coins and {xp_gained} XP!"
                
            else:
                description = f"{outcome['description']} You explored the {location}.\n"
                description += f"💰 Gained {format_number(coins_gained)} coins and {xp_gained} XP!"
                
            # Update player data
            player_data['coins'] += coins_gained
            player_data['xp'] += xp_gained
            player_data['adventure_count'] += 1
            player_data['last_adventure'] = datetime.now().isoformat()
            
            # Update stats
            if 'stats' not in player_data:
                player_data['stats'] = {}
            player_data['stats']['total_adventures'] = player_data['stats'].get('total_adventures', 0) + 1
            player_data['stats']['total_coins_earned'] = player_data['stats'].get('total_coins_earned', 0) + coins_gained
            player_data['stats']['total_xp_earned'] = player_data['stats'].get('total_xp_earned', 0) + xp_gained
            
            # Add items to inventory
            for item in items_found:
                if 'inventory' not in player_data:
                    player_data['inventory'] = []
                player_data['inventory'].append(item)
                
            # Check for level up
            level_up_msg = level_up_player(player_data)
            
            # Save data
            update_user_rpg_data(user_id, player_data)
            
            # Create response embed
            embed = create_embed(
                f"🎯 Adventure in {location}",
                description,
                COLORS['success']
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            
            if level_up_msg:
                embed.add_field(name="🎉 Level Up!", value=level_up_msg, inline=False)
                
            if damage_taken > 0:
                embed.add_field(
                    name="❤️ Health Status", 
                    value=f"HP: {player_data['hp']}/{player_data['max_hp']}", 
                    inline=False
                )
                
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in adventure command for {user_id}: {e}")
            await ctx.send("❌ An error occurred during your adventure. Please try again.")

    @commands.command(name='dungeon', aliases=['dg'], help='Enter a dangerous dungeon!')
    @commands.cooldown(1, RPG_CONSTANTS['dungeon_cooldown'], commands.BucketType.user)
    async def dungeon(self, ctx):
        """Dungeon command with higher risk and reward."""
        if not is_module_enabled("rpg_games", ctx.guild.id):
            return
            
        user_id = str(ctx.author.id)
        
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to `$start` your adventure first!")
            return
            
        try:
            player_data = get_user_rpg_data(user_id)
            
            if not player_data:
                await ctx.send("❌ Error retrieving player data. Please try again.")
                return
            
            # Require minimum level
            if player_data['level'] < 3:
                await ctx.send("❌ You need to be at least level 3 to enter dungeons!")
                return
                
            # Require minimum HP
            if player_data['hp'] < 50:
                await ctx.send("❌ You need at least 50 HP to enter a dungeon! Use `$heal` to restore health.")
                return
                
            # Dungeon simulation
            dungeon_type = random.choice(DUNGEON_TYPES)
            floors = random.randint(3, 7)
            total_coins = 0
            total_xp = 0
            damage_taken = 0
            items_found = []
            
            embed = discord.Embed(
                title=f"🏰 {dungeon_type}",
                description=f"You enter a {floors}-floor dungeon...",
                color=COLORS['primary']
            )
            
            # Simulate each floor
            for floor in range(1, floors + 1):
                floor_outcome = random.choices(
                    ["enemy", "trap", "treasure", "boss"],
                    weights=[40, 20, 30, 10 if floor == floors else 0]
                )[0]
                
                floor_coins = random.randint(30, 80)
                floor_xp = random.randint(20, 50)
                floor_damage = 0
                
                if floor_outcome == "enemy":
                    monster = random.choice(MONSTERS['uncommon'] if floor > 3 else MONSTERS['common'])
                    floor_damage = random.randint(10, 25)
                    embed.add_field(
                        name=f"Floor {floor} - {monster['name']}",
                        value=f"Defeated {monster['name']}!\n+{floor_coins} coins, +{floor_xp} XP\n-{floor_damage} HP",
                        inline=False
                    )
                    
                elif floor_outcome == "trap":
                    floor_damage = random.randint(15, 30)
                    floor_coins = random.randint(10, 40)
                    embed.add_field(
                        name=f"Floor {floor} - Trap",
                        value=f"Triggered a trap!\n+{floor_coins} coins, +{floor_xp} XP\n-{floor_damage} HP",
                        inline=False
                    )
                    
                elif floor_outcome == "treasure":
                    floor_coins = random.randint(50, 120)
                    if random.random() < 0.3:  # 30% chance for item
                        treasure_items = ['Magic Scroll', 'Gold Ring', 'Precious Stone', 'Ancient Artifact']
                        found_item = random.choice(treasure_items)
                        items_found.append(found_item)
                        embed.add_field(
                            name=f"Floor {floor} - Treasure",
                            value=f"Found treasure!\n+{floor_coins} coins, +{floor_xp} XP\n🎒 {found_item}",
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name=f"Floor {floor} - Treasure",
                            value=f"Found treasure!\n+{floor_coins} coins, +{floor_xp} XP",
                            inline=False
                        )
                        
                elif floor_outcome == "boss":
                    boss = random.choice(MONSTERS['rare'])
                    floor_coins = random.randint(100, 300)
                    floor_xp = random.randint(50, 100)
                    floor_damage = random.randint(20, 40)
                    boss_items = ['Legendary Sword', 'Dragon Scale Armor', 'Crown of Power', 'Mystic Staff']
                    found_item = random.choice(boss_items)
                    items_found.append(found_item)
                    embed.add_field(
                        name=f"Floor {floor} - Boss: {boss['name']}",
                        value=f"Defeated the boss!\n+{floor_coins} coins, +{floor_xp} XP\n-{floor_damage} HP\n🎒 {found_item}",
                        inline=False
                    )
                    
                total_coins += floor_coins
                total_xp += floor_xp
                damage_taken += floor_damage
                
            # Apply level bonus
            level_bonus = int(total_coins * 0.15 * player_data['level'])
            total_coins += level_bonus
            
            # Update player data
            player_data['coins'] += total_coins
            player_data['xp'] += total_xp
            player_data['hp'] = max(1, player_data['hp'] - damage_taken)
            player_data['dungeon_count'] += 1
            
            # Update stats
            if 'stats' not in player_data:
                player_data['stats'] = {}
            player_data['stats']['total_dungeons'] = player_data['stats'].get('total_dungeons', 0) + 1
            player_data['stats']['total_coins_earned'] = player_data['stats'].get('total_coins_earned', 0) + total_coins
            player_data['stats']['total_xp_earned'] = player_data['stats'].get('total_xp_earned', 0) + total_xp
            
            # Add items to inventory
            for item in items_found:
                if 'inventory' not in player_data:
                    player_data['inventory'] = []
                player_data['inventory'].append(item)
                
            # Check for level up
            level_up_msg = level_up_player(player_data)
            
            # Save data
            update_user_rpg_data(user_id, player_data)
            
            # Add summary
            embed.add_field(
                name="🎯 Dungeon Complete!",
                value=f"**Total Rewards:**\n"
                      f"💰 {format_number(total_coins)} coins\n"
                      f"⭐ {total_xp} XP\n"
                      f"❤️ {damage_taken} damage taken\n"
                      f"🎒 {len(items_found)} items found",
                inline=False
            )
            
            if level_up_msg:
                embed.add_field(name="🎉 Level Up!", value=level_up_msg, inline=False)
                
            embed.set_footer(text=f"Current HP: {player_data['hp']}/{player_data['max_hp']}")
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in dungeon command for {user_id}: {e}")
            await ctx.send("❌ An error occurred during your dungeon exploration. Please try again.")

    @commands.command(name='heal', help='Restore your health')
    @commands.cooldown(1, RPG_CONSTANTS['heal_cooldown'], commands.BucketType.user)
    async def heal(self, ctx):
        """Heal the player."""
        if not is_module_enabled("rpg_games", ctx.guild.id):
            return
            
        user_id = str(ctx.author.id)
        
        if not ensure_user_exists(user_id):
            await ctx.send("❌ You need to `$start` your adventure first!")
            return
            
        try:
            player_data = get_user_rpg_data(user_id)
            
            if not player_data:
                await ctx.send("❌ Error retrieving player data. Please try again.")
                return
            
            if player_data['hp'] >= player_data['max_hp']:
                await ctx.send("❤️ You're already at full health!")
                return
                
            # Heal to full
            old_hp = player_data['hp']
            player_data['hp'] = player_data['max_hp']
            healed = player_data['hp'] - old_hp
            
            # Save data
            update_user_rpg_data(user_id, player_data)
            
            embed = create_embed(
                "❤️ Healing Complete",
                f"You've been fully healed! Restored {healed} HP.\n"
                f"Current HP: {player_data['hp']}/{player_data['max_hp']}",
                COLORS['success']
            )
            
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in heal command for {user_id}: {e}")
            await ctx.send("❌ An error occurred while healing. Please try again.")

    @commands.command(name='leaderboard', aliases=['lb'], help='View the leaderboard')
    async def leaderboard(self, ctx, stat: str = "level"):
        """Display leaderboard."""
        if not is_module_enabled("rpg_games", ctx.guild.id):
            return
            
        valid_stats = ['level', 'coins', 'adventure_count', 'dungeon_count']
        if stat not in valid_stats:
            await ctx.send(f"❌ Invalid stat! Valid options: {', '.join(valid_stats)}")
            return
            
        try:
            from utils.database import get_leaderboard
            leaderboard_data = get_leaderboard(stat, 10)
            
            if not leaderboard_data:
                await ctx.send("❌ No leaderboard data available!")
                return
                
            embed = discord.Embed(
                title=f"🏆 {stat.title()} Leaderboard",
                color=COLORS['primary']
            )
            
            leaderboard_text = ""
            for i, entry in enumerate(leaderboard_data, 1):
                try:
                    user = await self.bot.fetch_user(int(entry['user_id']))
                    username = user.display_name
                except:
                    username = "Unknown User"
                    
                emoji = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
                leaderboard_text += f"{emoji} **{username}** - {format_number(entry['value'])}\n"
                
            embed.description = leaderboard_text
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in leaderboard command: {e}")
            await ctx.send("❌ An error occurred while fetching the leaderboard. Please try again.")

async def setup(bot):
    await bot.add_cog(RPGGamesCog(bot))
