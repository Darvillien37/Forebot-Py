from datetime import datetime, timezone
import discord

from Database import Database

DAILY = "daily"
WEEKLY = "weekly"
MONTHLY = "monthly"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

LAST_CLAIM_TIME = "last_claim"
CLAIM_READY_AT = "ready_at"
STREAK_EXPIRY_AT = "streak_expiry_at"
STREAK = "streak"


def find_default_channel(user, guild: discord.Guild):
    channel_id = Database.get_guild_spam_channel_id(guild.id)
    if channel_id is not None:
        channel = guild.get_channel(channel_id)
        if channel is not None:
            return channel

    channel = guild.system_channel  # getting system channel
    if (channel is None) or (not channel.permissions_for(user).send_messages):
        for c in guild.text_channels:  # get only text channels
            if c.permissions_for(guild.me).send_messages:  # check if bot has permissions
                channel = c
                break
    return channel


def to_unix_timestamp(timestamp: str) -> int:
    dt = datetime.strptime(timestamp, TIME_FORMAT).replace(tzinfo=timezone.utc)
    return int(dt.timestamp())
