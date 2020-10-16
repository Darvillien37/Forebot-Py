from discord.ext import commands
import discord
from Storage import Users


class Greetings(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.logger.info(f'{member.name} Joined Guild {member.guild.name}')
        # do nothing if it's a bot
        if member.bot:
            return
        Users.add_guild(member.id, member.guild.id)

        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('It\'s Ya Boi {0.mention}.'.format(member))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.logger.info(f'{member.name} Left Guild {member.guild.name}')
        Users.remove_guild(member.id, member.guild.id)

    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        """Says hello"""
        self.logger.info(f'{member.name} Triggered \'hello\'')
        member = member or ctx.author
        await ctx.send(f'Hello {member.mention}!')
