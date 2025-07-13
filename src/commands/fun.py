import discord
import os
from discord.ext import commands
import random

from Database import Database


class Fun(commands.Cog):
    def __init__(self, bot, res, logger):
        self.bot = bot
        self.res = res
        self.logger = logger

    # @commands.command(name='99', help='Responds with a random quote from '
    #                   'Brooklyn 99')
    # async def nine_nine(self, ctx):
    #     self.logger.info(f'{ctx.author.name} triggered \'99\' event')
    #     brooklyn_99_quotes = [
    #         'I\'m the human form of the 💯 emoji.',
    #         'Bingpot!',
    #         (
    #             'Cool. Cool cool cool cool cool cool cool, '
    #             'no doubt no doubt no doubt no doubt.'
    #         ),
    #     ]
    #     responce = random.choice(brooklyn_99_quotes)
    #     await ctx.send(responce)

    @commands.hybrid_command(name='roll', help='Roll some dice.')
    async def roll(self, ctx, number_of_dice: int, number_of_sides: int):
        self.logger.info(f'{ctx.author.name} triggered \'99 [{number_of_dice}]'
                         f'[{number_of_sides}]\' event')
        dice = [
            str(random.choice(range(1, number_of_sides + 1)))
            for _ in range(number_of_dice)
        ]
        await ctx.send(','.join(dice))

    @commands.hybrid_command(help='Gime a Foreman! Costs 10 💰!')
    async def foreman(self, ctx: commands.Context):
        coins = Database.get_coins(ctx.author.id)
        if coins >= 10:
            Database.update_coins(ctx.author.id, -10)
            files = os.listdir(self.res + '/Foremans/')
            d = random.choice(files)
            await ctx.send(
                file=discord.File(
                    os.path.abspath(self.res + '/Foremans/' + d)))
        else:
            await ctx.send("Ya Got No Coins! 😔")

    @commands.hybrid_command(help='Gime a Chaz!')
    async def chaz(self, ctx):
        files = os.listdir(self.res + '/Chaz/')
        d = random.choice(files)
        await ctx.send(
            file=discord.File(
                os.path.abspath(self.res + '/Chaz/' + d)))
