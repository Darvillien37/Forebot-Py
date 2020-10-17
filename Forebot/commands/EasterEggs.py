from discord.ext import commands


class EasterEggs(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    @commands.command(hidden=True)
    async def fuckUrMum4man(self, ctx):
        self.logger.info(f'{ctx.author.name} triggered "fuckUrMum4man" command')
        await ctx.send('FUCK YOUR MUM TWAT')

    @commands.command(hidden=True)
    async def KYS(self, ctx):
        self.logger.info(f'{ctx.author.name} triggered "KYS" command')
        await ctx.send(f"You'll miss me too much, {ctx.author.name}, ;)")

    @commands.command(hidden=True)
    async def forebot(self, ctx):
        self.logger.info(f'{ctx.author.name} triggered "forebot" command')
        await ctx.send("YOU WOT M80")

    @commands.command(hidden=True)
    async def drink(self, ctx):
        self.logger.info(f'{ctx.author.name} triggered "drink" command')
        await ctx.send("AHHH... The ice cold refreshment of Thatchers Haze")

    @commands.command(hidden=True)
    async def modest8(self, ctx):
        self.logger.info(f'{ctx.author.name} triggered "modest8" command')
        await ctx.send("Ohhh... Yes Please")

    @commands.command(hidden=True)
    async def Ping(self, ctx):
        self.logger.info(f'{ctx.author.name} triggered "Ping" command')
        await ctx.send(":ping_pong: Pong")

    @commands.command(hidden=True)
    async def Pong(self, ctx):
        self.logger.info(f'{ctx.author.name} triggered "Pong" command')
        await ctx.send(f":ping_pong: Ping: {self.bot.latency}")
