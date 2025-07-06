from discord.ext import commands


class EasterEggs(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    @commands.command(name="fuckurmum4man", hidden=True)
    async def fuck_ur_mum_4man(self, ctx):
        self.logger.info(f'{ctx.author.name} triggered "fuckUrMum4man" command')
        await ctx.send('FUCK YOUR MUM TWAT')

    @commands.command(hidden=True)
    async def kys(self, ctx):
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
    async def ping(self, ctx):
        self.logger.info(f'{ctx.author.name} triggered "Ping" command')
        await ctx.send(f":ping_pong: Pong {self.bot.latency}")

    @commands.command(hidden=True)
    async def pong(self, ctx):
        self.logger.info(f'{ctx.author.name} triggered "Pong" command')
        await ctx.send(":ping_pong: Ping ")
