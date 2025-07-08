from discord.ext import commands
import discord


class Greetings(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    @commands.hybrid_command()
    async def hello(self, ctx, *, member: discord.Member = None):
        """Says hello"""
        self.logger.info(f'{member.name} Triggered \'hello\'')
        member = member or ctx.author
        await ctx.send(f'Hello {member.mention}!')
