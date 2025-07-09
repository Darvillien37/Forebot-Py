import discord

from Database import Database

DAILY = "daily"
WEEKLY = "weekly"
MONTHLY = "monthly"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def find_default_channel(user, guild: discord.Guild):
    channel = Database.get_guild_spam_channel_id(guild.id)
    if channel is not None:
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
