from discord.ext import commands
import discord
from Database import Database


class Admin(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    @commands.hybrid_command(help='Set the text channel for bot spam. Uses System Channel by default.')
    @commands.has_permissions(manage_channels=True)
    async def set_bot_spam_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        if channel in ctx.guild.channels:
            Database.set_guild_spam_channel_id(ctx.guild.id, channel.id)
            await ctx.send(f"Bot Spam Channel set to {channel.mention}", ephemeral=True)
        else:
            await ctx.send("You Wot? that channels not in this server?", ephemeral=True)
