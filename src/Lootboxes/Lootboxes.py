from Database import Database
from Lootboxes import HandleTierClaim
from Lootboxes.ClaimNowButton import ClaimNowButton
from Lootboxes.ClaimView import LootboxClaimView
from discord.ext import commands
import discord
from datetime import datetime, timezone, timedelta
from Utils.utils import DAILY, WEEKLY, MONTHLY, TIME_FORMAT


class Lootboxes(commands.Cog):

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.BOX_DELTAS = {
            DAILY: timedelta(days=1),
            WEEKLY: timedelta(weeks=1),
            MONTHLY: timedelta(days=30),
        }

    @commands.hybrid_command(aliases=['lootbox', 'boxes'], help="View and Claim your lootboxes.")
    async def lootboxes(self, ctx):
        user = ctx.author
        box_counts = Database.get_lootboxes(user.id)
        if not box_counts:
            await ctx.send("User not found.")
            return

        embed = discord.Embed(
            title=f"{user.display_name}'s Lootboxes",
            color=discord.Color.blurple()
        )

        for tier in box_counts:
            emoji = Database.LOOT_TIERS[tier]["emoji"]
            embed.add_field(name=f"{emoji} {tier.title()}", value=str(box_counts[tier]), inline=True)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        message = await ctx.send(embed=embed)

        view = LootboxClaimView(
            bot=self.bot,
            user_id=user.id,
            boxes=box_counts,
            cog_ref=self,
            original_embed=embed,
            original_message=message
        )
        await message.edit(view=view)

    @commands.hybrid_command(help="Open your best available lootbox!")
    async def claim(self, ctx: commands.Context):
        result = Database.get_highest_tier_lootbox(ctx.author.id)
        if result is None:
            await ctx.send("❌ You don't have any lootboxes to claim.", ephemeral=True)
            return

        tier = result
        await HandleTierClaim.handle_tier_claim(tier, ctx)

    @commands.hybrid_command(help="Open all your lootboxes!")
    async def claim_all(self, ctx: commands.Context):
        user_id = ctx.author.id
        boxes = Database.get_lootboxes(user_id)

        if not any(count > 0 for count in boxes.values()):
            await ctx.send("❌ You have no lootboxes to claim.", ephemeral=True)
            return

        total_coins = 0
        claimed_boxes = []
        for tier, count in boxes.items():
            tier_total = 0
            for _ in range(count):
                reward = Database.claim_specific_lootbox(user_id, tier)
                if reward is not None:
                    total_coins += reward
                    tier_total += reward
            if count > 0:
                claimed_boxes.append((tier, count, tier_total))

        # Build and send summary embed
        embed = discord.Embed(
            title="🎁 All Lootboxes Claimed!",
            description=f"You gained **{total_coins} Forecoins**!",
            color=discord.Color.blurple(),
            timestamp=datetime.now(timezone.utc)
        )

        for tier, count, tier_total in claimed_boxes:
            emoji = Database.LOOT_TIERS[tier]["emoji"]
            embed.add_field(name=f"{emoji} {count}x {tier.title()}", value=f"💰 {tier_total} Forecoins", inline=True)

        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name=DAILY, description="Claim your daily lootbox.")
    async def daily(self, ctx: commands.Context):
        await self.handle_periodic_claim(ctx, DAILY)

    @commands.hybrid_command(name=WEEKLY, description="Claim your weekly lootbox.")
    async def weekly(self, ctx: commands.Context):
        await self.handle_periodic_claim(ctx, WEEKLY)

    @commands.hybrid_command(name=MONTHLY, description="Claim your monthly lootbox.")
    async def monthly(self, ctx: commands.Context):
        await self.handle_periodic_claim(ctx, MONTHLY)

    async def handle_periodic_claim(self, ctx, period_type):
        user_id = ctx.author.id
        remaining = self.time_until_claim(user_id, period_type)
        if remaining.total_seconds() > 0:
            time_str = format_timedelta(remaining)
            await ctx.send(f"⏳ You can claim your next {period_type} lootbox in **{time_str}**.")
            return

        tier = Database.roll_loot_tier()
        Database.add_lootbox(user_id, tier)
        Database.update_claim_timestamp(user_id, period_type)

        embed = discord.Embed(
            title=f"🎁 {period_type.title()} Lootbox Claimed!",
            description=f"You received a **{tier.title()}** lootbox!",
            color=Database.LOOT_TIERS[tier]["color"]
        )
        message = await ctx.send(embed=embed)
        claimBtn = ClaimNowButton(user_id, tier, message)
        await message.edit(view=claimBtn)

    def time_until_claim(self, user_id, period_type):
        timestamps = Database.get_claim_timestamps(user_id)
        if not timestamps or not timestamps[period_type]:
            return timedelta(0)

        last_dt = datetime.strptime(timestamps[period_type], TIME_FORMAT).replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)

        delta = self.BOX_DELTAS[period_type]

        next_time = last_dt + delta
        remaining = next_time - now
        return max(timedelta(0), remaining)


def format_timedelta(td: timedelta):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours >= 24:
        days, hours = divmod(hours, 24)
        return f"{days}d {hours}h"
    elif hours:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m {seconds}s"
