from logging import Logger
import os
import random
from Database import Database, Items
from Database.attributes import ATTR_LUCK
from Utils import LootboxGraph
from Utils import utils
from views.ClaimView import LootboxClaimView
from discord.ext import commands
import discord
from datetime import datetime, timezone, timedelta
from Utils.utils import DAILY, WEEKLY, MONTHLY, TIME_FORMAT
from Utils.utils import LAST_CLAIM_TIME, CLAIM_READY_AT, STREAK_EXPIRY_AT, STREAK
from commands import lootboxes as LB


TIME_DELTA = "time_delta"
EMOJI = "emoji"
STREAK_GRACE_DELTA = "streak_grace"
STREAK_BONUS_MULTI = "streak_bonus_multi"
CLAIM_TYPE_DATA = {
    DAILY: {TIME_DELTA: timedelta(days=1),    STREAK_GRACE_DELTA: timedelta(hours=6), STREAK_BONUS_MULTI: 0.01, EMOJI: ":sunny:"},
    WEEKLY: {TIME_DELTA: timedelta(weeks=1),  STREAK_GRACE_DELTA: timedelta(days=1),  STREAK_BONUS_MULTI: 0.1,  EMOJI: ":seven:"},
    MONTHLY: {TIME_DELTA: timedelta(days=30), STREAK_GRACE_DELTA: timedelta(days=3),  STREAK_BONUS_MULTI: 1,    EMOJI: ":calendar_spiral:"}
}


class Lootboxes(commands.Cog):
    def __init__(self, bot, logger: Logger):
        self.bot = bot
        self.logger = logger

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
            emoji = Items.LOOT_TIERS[tier]["emoji"]
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

    @commands.hybrid_command(help="Open all your lootboxes!")
    async def open_all(self, ctx: commands.Context):
        user_id = ctx.author.id
        boxes = Database.get_lootboxes(user_id)

        if not any(count > 0 for count in boxes.values()):
            await ctx.send("❌ You have no lootboxes to claim.", ephemeral=True)
            return
        msg = await ctx.send("Opening your Lootboxes...")
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
            emoji = Items.LOOT_TIERS[tier]["emoji"]
            embed.add_field(name=f"{emoji} {count}x {tier.title()}", value=f"💰 {tier_total} Forecoins", inline=True)

        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await msg.edit(content=None, embed=embed)

    @commands.hybrid_command(help="Claim your Daily, Weekly, and Monthly Lootboxes!")
    async def claim(self, ctx: commands.Context):
        user_id = ctx.author.id
        embed = discord.Embed(
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)

        any_gained = False
        # extract claim timestamp data from DB for all types
        # Dont forget: times in dictionary are a string, not datetime format
        user_time_data = Database.get_claim_timestamps(user_id)
        user_attributes = Database.get_user_attributes(user_id)
        NOW = datetime.now(timezone.utc)
        for period_type in CLAIM_TYPE_DATA:
            # x_streak, x_last_claim, x_claim_ready_at, x_streak_expiry_at
            # Check if can claim
            if user_time_data[period_type][CLAIM_READY_AT] is None:
                ts_claim_ready_at = NOW
            else:
                ts_claim_ready_at = datetime.strptime(user_time_data[period_type][CLAIM_READY_AT], TIME_FORMAT).replace(tzinfo=timezone.utc)
            if user_time_data[period_type][STREAK_EXPIRY_AT] is None:
                ts_streak_expiry_at = NOW
            else:
                ts_streak_expiry_at = datetime.strptime(user_time_data[period_type][STREAK_EXPIRY_AT], TIME_FORMAT).replace(tzinfo=timezone.utc)

            if NOW >= ts_claim_ready_at:
                # Can claim.
                # Check to maintain streak.
                streak_lost_str = ""
                if NOW > ts_streak_expiry_at:
                    # Expired streak
                    user_time_data[period_type][STREAK] = 0
                    streak_lost_str = "Lost 😞 "  # need that space at the end of string
                else:
                    user_time_data[period_type][STREAK] += 1

                # set x_last_claim to now()
                user_time_data[period_type][LAST_CLAIM_TIME] = NOW.strftime(TIME_FORMAT)
                # calculate time user can next claim this type, and time the streak expires
                ts_next_time_avail = self.calculate_claim_time_available(NOW, period_type, user_attributes)
                user_time_data[period_type][CLAIM_READY_AT] = ts_next_time_avail.strftime(TIME_FORMAT)
                ts_streak_expiry_at = self.calculate_streak_expiry_time(ts_next_time_avail, period_type, user_attributes)
                user_time_data[period_type][STREAK_EXPIRY_AT] = ts_streak_expiry_at.strftime(TIME_FORMAT)

                # TIME TO ROLL
                box_tier, _ = roll_lootbox_tier(period_type, user_time_data[period_type][STREAK], user_attributes)

                Database.add_lootbox(user_id, box_tier)
                Database.update_claim_timestamp(user_id, period_type, user_time_data[period_type])
                any_gained = True
                box_emoji = Items.LOOT_TIERS[box_tier]["emoji"]
                embed.add_field(name=f"{CLAIM_TYPE_DATA[period_type][EMOJI]} {period_type.title()}",
                                value=(
                                    f"{box_emoji} {box_tier.title()} Gained!\n"
                                    f"- Streak {streak_lost_str}{user_time_data[period_type][STREAK]}\n"
                                    f"- Next Claim <t:{utils.to_unix_timestamp(user_time_data[period_type][CLAIM_READY_AT])}:R>\n"
                                    f"- Keep Streak by <t:{utils.to_unix_timestamp(user_time_data[period_type][STREAK_EXPIRY_AT])}:R>"
                                ),
                                inline=True)
            else:
                # Cannot Claim
                embed.add_field(name=f"{CLAIM_TYPE_DATA[period_type][EMOJI]} {period_type.title()}",
                                value=(
                                    f"Too Early!\n"
                                    f"Streak **{user_time_data[period_type][STREAK]}**\n"
                                    f"Next Claim <t:{utils.to_unix_timestamp(user_time_data[period_type][CLAIM_READY_AT])}:R>\n"
                                    f"Keep Streak by <t:{utils.to_unix_timestamp(user_time_data[period_type][STREAK_EXPIRY_AT])}:R>"
                                ),
                                inline=True)

        if any_gained:
            embed.title = "🎁 Lootboxes Claimed!"
            embed.description = "You received some Lootboxes!\nType '/boxes' to view them"
            embed.description += "\nor '/open_all' to open them now!"
        else:
            embed.title = "😔 No Lootboxes yet"
            embed.description = "Try again later!"

        await ctx.send(embed=embed)

    @commands.hybrid_command(help="Check the chances of the next Lootbox you could get.")
    async def claim_chances(self, ctx: commands.Context):
        name, fig = LootboxGraph.get_graph(ctx.author.id)
        image_name = f"{name}.png"
        fig.savefig(image_name, dpi=300, bbox_inches='tight')
        await ctx.send(file=discord.File(os.path.abspath(f'./{image_name}')))
        os.remove(f'./{image_name}')
        pass

    def calculate_claim_time_available(self, now: datetime, period_type: str, user_attributes) -> datetime:
        return now + CLAIM_TYPE_DATA[period_type][TIME_DELTA]

    def calculate_streak_expiry_time(self, avail_at: datetime, period_type: str, user_attributes) -> datetime:
        return avail_at + CLAIM_TYPE_DATA[period_type][STREAK_GRACE_DELTA]


def roll_lootbox_tier(period_type: str, streak: int, user_attributes):
    weights = {}
    for tier in Items.LOOT_TIERS:
        weights[tier] = Items.LOOT_TIERS[tier]['weight']
    # print(f"base Weights:\t\t{weights}")

    # Apply period_type modifiers
    for tier in Items.LOOT_TIERS:
        if period_type == WEEKLY:
            if tier in [Items.TIER_RARE, Items.TIER_EPIC, Items.TIER_LEGENDARY, Items.TIER_MYTHIC]:
                weights[tier] *= 1.2
        if period_type == MONTHLY:
            if tier in [Items.TIER_EPIC, Items.TIER_LEGENDARY, Items.TIER_MYTHIC]:
                weights[tier] *= 1.5
    # print(f"period_type Weights:\t{weights}")

    # apply streak
    for tier in Items.LOOT_TIERS:
        if tier not in [Items.TIER_COMMON, Items.TIER_UNCOMMON]:
            weights[tier] *= min(100, 1 + (streak * LB.CLAIM_TYPE_DATA[period_type][STREAK_BONUS_MULTI]))
    # print(f"streak Weights:\t\t{weights}")

    # apply attribute modifiers
    for tier in Items.LOOT_TIERS:
        if tier == Items.TIER_COMMON:
            weights[tier] *= (1 - (user_attributes[ATTR_LUCK] * 0.01))
        if tier == Items.TIER_UNCOMMON:
            weights[tier] *= (1 - (user_attributes[ATTR_LUCK] * 0.005))
        elif tier in ["rare", "epic", "legendary", "mythic"]:
            weights[tier] *= (1 + (user_attributes[ATTR_LUCK] * 0.005))
        if user_attributes[ATTR_LUCK] >= 100:
            if tier in ["legendary", "mythic"]:
                weights[tier] *= (1 + (user_attributes[ATTR_LUCK] * 0.005))

        if weights[tier] < 0:
            weights[tier] = 0
    # print(f"luck Weights:\t\t{weights}")

    tiers = list(weights.keys())
    w = list(weights.values())
    chosen = random.choices(tiers, weights=w, k=1)[0]
    # print(f"Chosen:{chosen}")
    return chosen, weights


# Streak grace period recovery system that accounts for bot downtime
# so users aren’t unfairly punished for missing streaks due to the bot being offline.
def streak_grace_recovery(logger: Logger):
    # Get last heartbeat
    last_hb_str = Database.get_last_heartbeat()
    if not last_hb_str:
        logger.error("[Streak Recovery] No last heartbeat found, skipping.")
        return
    last_hb = datetime.strptime(last_hb_str, TIME_FORMAT).replace(tzinfo=timezone.utc)
    # calculate the downtime of the bot
    now = datetime.now(timezone.utc)
    downtime = now - last_hb
    DOWNTIME_THRESHOLD = timedelta(hours=1.5)
    if downtime <= DOWNTIME_THRESHOLD:
        logger.debug("[Streak Recovery] Downtime below threshold, skipping.")
        return
    logger.info(f"[Streak Recovery] Downtime detected: {downtime}")

    # Dont forget: times in dictionary are a string, not datetime format
    streak_expires = Database.get_all_claim_streak_expires()
    if streak_expires is None:
        logger.debug("[Streak Recovery] No Claim Data Detected.")
        return

    updated_counters = {DAILY: 0, WEEKLY: 0, MONTHLY: 0}
    data_updated = False

    # loop through all data received and check...
    for id in streak_expires:
        if id is None:
            continue
        for type in streak_expires[id]:
            if streak_expires[id][type] is None:
                continue
            expiry_ts = datetime.strptime(streak_expires[id][type], TIME_FORMAT).replace(tzinfo=timezone.utc)
            # Check if the streak was missed purely because of downtime
            if now > expiry_ts and last_hb < expiry_ts:
                # add time between last_hb and the expiry time
                new_deadline = now + (expiry_ts-last_hb)
                streak_expires[id][type] = new_deadline.strftime(TIME_FORMAT)
                updated_counters[type] = updated_counters[type] + 1
                data_updated = True
    logger.info("[Streak Recovery] Extended streak deadlines for "
                f"{updated_counters[DAILY]} Daily, {updated_counters[WEEKLY]} Weekly, {updated_counters[MONTHLY]} Monthly.")

    if data_updated:
        Database.update_claim_streak_expires(streak_expires)
