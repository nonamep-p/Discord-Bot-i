import discord
from discord.ext import commands
import random
from datetime import datetime, timedelta
from replit import db
from utils.database import get_user_data, update_user_data, ensure_user_exists, get_user_rpg_data, update_user_rpg_data
from utils.helpers import create_embed, format_number, level_up_player, get_random_work_job, get_time_until_next_use, format_time_remaining
from utils.constants import SHOP_ITEMS, ITEMS, RPG_CONSTANTS, DAILY_REWARDS
from config import COLORS, EMOJIS, is_module_enabled
import logging

logger = logging.getLogger(__name__)

class EconomyCog(commands.Cog):
    """Economy and shop system for the bot."""
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='work', help='Work to earn coins')
    @commands.cooldown(1, RPG_CONSTANTS['work_cooldown'], commands.BucketType.user)
    async def work(self, ctx):
        """Work to earn coins."""
        if not is_module_enabled("economy", ctx.guild.id):
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
            
            # Get random job
            job = get_random_work_job()
            coins_earned = random.randint(job["min_coins"], job["max_coins"])
            xp_earned = random.randint(job["min_xp"], job["max_xp"])
            
            # Level bonus
            level_bonus = int(coins_earned * 0.1 * player_data['level'])
            coins_earned += level_bonus
            
            # Update player data
            player_data['coins'] += coins_earned
            player_data['xp'] += xp_earned
            player_data['last_work'] = datetime.now().isoformat()
            player_data['work_count'] = player_data.get('work_count', 0) + 1
            
            # Update stats
            if 'stats' not in player_data:
                player_data['stats'] = {}
            player_data['stats']['total_coins_earned'] = player_data['stats'].get('total_coins_earned', 0) + coins_earned
            player_data['stats']['total_xp_earned'] = player_data['stats'].get('total_xp_earned', 0) + xp_earned
            
            # Check for level up
            level_up_msg = level_up_player(player_data)
                
            # Save data
            update_user_rpg_data(user_id, player_data)
            
            embed = create_embed(
                f"💼 Work Complete!",
                f"You worked as a **{job['name']}** and earned:\n"
                f"💰 {format_number(coins_earned)} coins\n"
                f"⭐ {xp_earned} XP\n\n"
                f"Total coins: {format_number(player_data['coins'])}",
                COLORS['success']
            )
            
            if level_up_msg:
                embed.add_field(name="🎉 Level Up!", value=level_up_msg, inline=False)
                
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in work command for {user_id}: {e}")
            await ctx.send("❌ An error occurred while working. Please try again.")
        
    @commands.command(name='daily', help='Claim your daily reward')
    @commands.cooldown(1, RPG_CONSTANTS['daily_cooldown'], commands.BucketType.user)
    async def daily_reward(self, ctx):
        """Claim daily reward."""
        if not is_module_enabled("economy", ctx.guild.id):
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
            
            # Daily reward based on level
            base_reward = DAILY_REWARDS['base']
            level_bonus = player_data['level'] * DAILY_REWARDS['level_multiplier']
            total_reward = base_reward + level_bonus
            
            # Random bonus
            bonus_chance = random.randint(1, 100)
            bonus_text = ""
            if bonus_chance <= 20:  # 20% chance
                bonus_amount = random.randint(100, 500)
                total_reward += bonus_amount
                bonus_text = f"\n🎲 Lucky bonus: +{bonus_amount} coins!"
                
            # Update player data
            player_data['coins'] += total_reward
            player_data['last_daily'] = datetime.now().isoformat()
            
            # Update stats
            if 'stats' not in player_data:
                player_data['stats'] = {}
            player_data['stats']['total_coins_earned'] = player_data['stats'].get('total_coins_earned', 0) + total_reward
            
            # Save data
            update_user_rpg_data(user_id, player_data)
            
            embed = create_embed(
                "🎁 Daily Reward Claimed!",
                f"You received **{format_number(total_reward)}** coins!\n"
                f"Base reward: {base_reward}\n"
                f"Level bonus: {level_bonus}{bonus_text}\n\n"
                f"Total coins: {format_number(player_data['coins'])}",
                COLORS['warning']
            )
            
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in daily command for {user_id}: {e}")
            await ctx.send("❌ An error occurred while claiming daily reward. Please try again.")
        
    @commands.command(name='shop', help='View the item shop')
    async def shop(self, ctx):
        """Display the item shop."""
        if not is_module_enabled("economy", ctx.guild.id):
            return
            
        try:
            embed = discord.Embed(
                title="🏪 Item Shop",
                description="Use `$buy <item>` to purchase items",
                color=COLORS['info']
            )
            
            for category, items in SHOP_ITEMS.items():
                item_list = []
                for item_name, item_data in items.items():
                    price = item_data.get('price', 0)
                    rarity = item_data.get('rarity', 'common')
                    rarity_emoji = {'common': '⚪', 'uncommon': '🟢', 'rare': '🔵', 'epic': '🟣', 'legendary': '🟡'}.get(rarity, '⚪')
                    item_list.append(f"{rarity_emoji} **{item_name}** - 💰 {format_number(price)}")
                    
                embed.add_field(
                    name=f"{category.title()}",
                    value="\n".join(item_list),
                    inline=False
                )
                
            embed.set_footer(text="Prices may vary. Higher level items unlock as you progress!")
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in shop command: {e}")
            await ctx.send("❌ An error occurred while displaying the shop. Please try again.")
        
    @commands.command(name='buy', help='Buy an item from the shop')
    async def buy_item(self, ctx, *, item_name: str):
        """Buy an item from the shop."""
        if not is_module_enabled("economy", ctx.guild.id):
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
            
            # Find item in shop
            found_item = None
            item_category = None
            
            for category, items in SHOP_ITEMS.items():
                for shop_item, item_data in items.items():
                    if shop_item.lower() == item_name.lower():
                        found_item = shop_item
                        item_category = category
                        break
                if found_item:
                    break
                    
            if not found_item:
                await ctx.send("❌ Item not found in shop! Use `$shop` to see available items.")
                return
                
            item_data = SHOP_ITEMS[item_category][found_item]
            price = item_data['price']
            
            # Check if player has enough coins
            if player_data['coins'] < price:
                await ctx.send(f"❌ You don't have enough coins! You need {format_number(price)} coins but only have {format_number(player_data['coins'])}.")
                return
                
            # Check inventory space
            if len(player_data.get('inventory', [])) >= RPG_CONSTANTS['max_inventory_size']:
                await ctx.send("❌ Your inventory is full! Sell some items first.")
                return
                
            # Process purchase
            player_data['coins'] -= price
            if 'inventory' not in player_data:
                player_data['inventory'] = []
            player_data['inventory'].append(found_item)
            
            # Save data
            update_user_rpg_data(user_id, player_data)
            
            embed = create_embed(
                "✅ Purchase Successful!",
                f"You bought **{found_item}** for {format_number(price)} coins!\n\n"
                f"Remaining coins: {format_number(player_data['coins'])}",
                COLORS['success']
            )
            
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in buy command for {user_id}: {e}")
            await ctx.send("❌ An error occurred while purchasing the item. Please try again.")
        
    @commands.command(name='sell', help='Sell items from your inventory')
    async def sell_item(self, ctx, *, item_name: str):
        """Sell an item from inventory."""
        if not is_module_enabled("economy", ctx.guild.id):
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
            
            # Check if item is in inventory
            if 'inventory' not in player_data:
                player_data['inventory'] = []
                
            if item_name not in player_data['inventory']:
                await ctx.send("❌ You don't have that item in your inventory!")
                return
                
            # Find item data to determine sell price
            sell_price = 0
            for category, items in SHOP_ITEMS.items():
                if item_name in items:
                    sell_price = int(items[item_name]['price'] * 0.6)  # 60% of buy price
                    break
                    
            if sell_price == 0:
                # Default sell price for non-shop items
                sell_price = random.randint(10, 50)
                
            # Process sale
            player_data['inventory'].remove(item_name)
            player_data['coins'] += sell_price
            
            # Save data
            update_user_rpg_data(user_id, player_data)
            
            embed = create_embed(
                "💰 Item Sold!",
                f"You sold **{item_name}** for {format_number(sell_price)} coins!\n\n"
                f"Total coins: {format_number(player_data['coins'])}",
                COLORS['success']
            )
            
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in sell command for {user_id}: {e}")
            await ctx.send("❌ An error occurred while selling the item. Please try again.")
        
    @commands.command(name='use', help='Use an item from your inventory')
    async def use_item(self, ctx, *, item_name: str):
        """Use an item from inventory."""
        if not is_module_enabled("economy", ctx.guild.id):
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
            
            # Check if item is in inventory
            if 'inventory' not in player_data:
                player_data['inventory'] = []
                
            if item_name not in player_data['inventory']:
                await ctx.send("❌ You don't have that item in your inventory!")
                return
                
            # Process item usage
            result_text = ""
            item_consumed = True
            
            # Health potions
            if any(potion in item_name.lower() for potion in ['health potion', 'healing potion', 'greater health potion']):
                heal_amount = 50 if 'greater' in item_name.lower() else 30
                heal_amount += random.randint(-5, 10)  # Small variance
                
                old_hp = player_data['hp']
                player_data['hp'] = min(player_data['max_hp'], player_data['hp'] + heal_amount)
                actual_heal = player_data['hp'] - old_hp
                
                if actual_heal > 0:
                    result_text = f"❤️ Healed for {actual_heal} HP! (HP: {player_data['hp']}/{player_data['max_hp']})"
                else:
                    result_text = f"❤️ You're already at full health!"
                    item_consumed = False
                    
            # Strength potions
            elif any(potion in item_name.lower() for potion in ['strength potion', 'power potion']):
                result_text = "⚔️ You feel stronger! (Effect would last for next adventure)"
                
            # Magic rings
            elif any(ring in item_name.lower() for ring in ['magic ring', 'enchanted ring']):
                stat_boost = random.randint(2, 5)
                boost_type = random.choice(['attack', 'defense', 'max_hp'])
                
                if boost_type == 'max_hp':
                    player_data['max_hp'] += stat_boost
                    player_data['hp'] = min(player_data['hp'] + stat_boost, player_data['max_hp'])
                    result_text = f"✨ Your maximum HP increased by {stat_boost}! (Max HP: {player_data['max_hp']})"
                elif boost_type == 'attack':
                    player_data['attack'] += stat_boost
                    result_text = f"✨ Your attack increased by {stat_boost}! (Attack: {player_data['attack']})"
                else:
                    player_data['defense'] += stat_boost
                    result_text = f"✨ Your defense increased by {stat_boost}! (Defense: {player_data['defense']})"
                    
            # Weapons
            elif any(weapon in item_name.lower() for weapon in ['sword', 'blade', 'dagger', 'axe']):
                # Find weapon stats
                weapon_stats = None
                for category, items in ITEMS.items():
                    if item_name in items:
                        weapon_stats = items[item_name]
                        break
                        
                if weapon_stats and 'attack' in weapon_stats:
                    old_weapon = player_data.get('equipped', {}).get('weapon')
                    
                    if 'equipped' not in player_data:
                        player_data['equipped'] = {}
                        
                    player_data['equipped']['weapon'] = item_name
                    
                    # Calculate attack bonus
                    attack_bonus = weapon_stats['attack']
                    player_data['attack'] += attack_bonus
                    
                    result_text = f"⚔️ Equipped {item_name}! Attack increased by {attack_bonus}!"
                    
                    if old_weapon:
                        player_data['inventory'].append(old_weapon)
                        result_text += f" (Previous weapon {old_weapon} returned to inventory)"
                        
                    item_consumed = False
                else:
                    result_text = f"⚔️ You equipped {item_name}!"
                    item_consumed = False
                    
            # Armor
            elif any(armor in item_name.lower() for armor in ['armor', 'shield', 'mail']):
                # Find armor stats
                armor_stats = None
                for category, items in ITEMS.items():
                    if item_name in items:
                        armor_stats = items[item_name]
                        break
                        
                if armor_stats and 'defense' in armor_stats:
                    old_armor = player_data.get('equipped', {}).get('armor')
                    
                    if 'equipped' not in player_data:
                        player_data['equipped'] = {}
                        
                    player_data['equipped']['armor'] = item_name
                    
                    # Calculate defense bonus
                    defense_bonus = armor_stats['defense']
                    player_data['defense'] += defense_bonus
                    
                    result_text = f"🛡️ Equipped {item_name}! Defense increased by {defense_bonus}!"
                    
                    if old_armor:
                        player_data['inventory'].append(old_armor)
                        result_text += f" (Previous armor {old_armor} returned to inventory)"
                        
                    item_consumed = False
                else:
                    result_text = f"🛡️ You equipped {item_name}!"
                    item_consumed = False
                    
            # Scrolls and special items
            elif 'scroll' in item_name.lower():
                if 'ancient' in item_name.lower():
                    xp_bonus = random.randint(50, 150)
                    player_data['xp'] += xp_bonus
                    result_text = f"📜 You learned from the ancient scroll! Gained {xp_bonus} XP!"
                else:
                    result_text = f"📜 You read the scroll and gained knowledge!"
                    
            else:
                result_text = f"🤷 You used {item_name} but nothing obvious happened..."
                
            # Remove item from inventory if consumed
            if item_consumed:
                player_data['inventory'].remove(item_name)
                
            # Check for level up
            level_up_msg = level_up_player(player_data)
                
            # Save data
            update_user_rpg_data(user_id, player_data)
            
            embed = create_embed(
                f"🎯 Used {item_name}",
                result_text,
                COLORS['info']
            )
            
            if level_up_msg:
                embed.add_field(name="🎉 Level Up!", value=level_up_msg, inline=False)
            
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in use command for {user_id}: {e}")
            await ctx.send("❌ An error occurred while using the item. Please try again.")
        
    @commands.command(name='balance', aliases=['bal'], help='Check your coin balance')
    async def balance(self, ctx, member: discord.Member = None):
        """Check coin balance."""
        if not is_module_enabled("economy", ctx.guild.id):
            return
            
        target = member or ctx.author
        user_id = str(target.id)
        
        if not ensure_user_exists(user_id):
            if target == ctx.author:
                await ctx.send("❌ You need to `$start` your adventure first!")
            else:
                await ctx.send("❌ That user hasn't started their adventure yet!")
            return
            
        try:
            player_data = get_user_rpg_data(user_id)
            
            if not player_data:
                await ctx.send("❌ Error retrieving player data. Please try again.")
                return
            
            embed = create_embed(
                f"💰 {target.display_name}'s Balance",
                f"**Coins:** {format_number(player_data['coins'])}\n"
                f"**Level:** {player_data['level']}\n"
                f"**Total Adventures:** {player_data.get('adventure_count', 0)}\n"
                f"**Work Sessions:** {player_data.get('work_count', 0)}",
                COLORS['warning']
            )
            embed.set_thumbnail(url=target.display_avatar.url)
            
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in balance command for {user_id}: {e}")
            await ctx.send("❌ An error occurred while checking balance. Please try again.")
        
    @commands.command(name='inventory', aliases=['inv'], help='View your inventory')
    async def inventory(self, ctx):
        """View player inventory."""
        if not is_module_enabled("economy", ctx.guild.id):
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
            
            inventory = player_data.get('inventory', [])
            
            embed = discord.Embed(
                title=f"🎒 {ctx.author.display_name}'s Inventory",
                color=COLORS['secondary']
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            
            if not inventory:
                embed.description = "Your inventory is empty! Go on adventures or buy items from the shop."
            else:
                # Group items by count
                item_counts = {}
                for item in inventory:
                    item_counts[item] = item_counts.get(item, 0) + 1
                    
                # Sort items by count (most common first)
                sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
                
                # Create inventory display
                inventory_text = ""
                for item, count in sorted_items:
                    if count > 1:
                        inventory_text += f"• **{item}** x{count}\n"
                    else:
                        inventory_text += f"• **{item}**\n"
                        
                embed.description = inventory_text
                
            embed.add_field(
                name="📊 Inventory Stats",
                value=f"**Items:** {len(inventory)}/{RPG_CONSTANTS['max_inventory_size']}\n"
                      f"**Unique Items:** {len(set(inventory)) if inventory else 0}",
                inline=False
            )
            
            embed.set_footer(text="Use $use <item> to use items or $sell <item> to sell them")
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in inventory command for {user_id}: {e}")
            await ctx.send("❌ An error occurred while viewing inventory. Please try again.")

async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
