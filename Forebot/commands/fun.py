import discord
import os
from discord.ext import commands
import random


class Fun(commands.Cog):
    def __init__(self, bot, res):
        self.bot = bot
        self.res = res

    @commands.command(name='99', help='Responds with a random quote from \
Brooklyn 99')
    async def nine_nine(self, ctx):
        brooklyn_99_quotes = [
            'I\'m the human form of the 💯 emoji.',
            'Bingpot!',
            (
                'Cool. Cool cool cool cool cool cool cool, '
                'no doubt no doubt no doubt no doubt.'
            ),
        ]
        responce = random.choice(brooklyn_99_quotes)
        await ctx.send(responce)

    @commands.command(name='roll', help='Roll some dice.')
    async def roll(self, ctx, number_of_dice: int, number_of_sides: int):
        dice = [
            str(random.choice(range(1, number_of_sides + 1)))
            for _ in range(number_of_dice)
        ]
        await ctx.send(','.join(dice))

    @commands.command(help='Responds with a Foreman!')
    async def foreman(self, ctx):
        files = os.listdir(self.res)
        d = random.choice(files)
        await ctx.message.delete()
        await ctx.send(
            file=discord.File(
                os.path.abspath(self.res + d)))
