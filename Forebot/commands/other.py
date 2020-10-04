from discord.ext import commands


class Other(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    @commands.command(help='Check the progress of Forebots development')
    async def trello(self, ctx):
        self.logger.info(f'{ctx.author.name} triggered \'trello\' command')
        await ctx.message.delete()
        await ctx.send("Link to the Forebot trello board:"
                       " https://trello.com/b/GO9a8ZAd")

    @commands.command(help='link to 4bot source code')
    async def github(self, ctx):
        self.logger.info(f'{ctx.author.name} triggered \'github\' command')
        await ctx.message.delete()
        await ctx.send("Link to the Forebot github:"
                       " https://github.com/Darvillien37/Forebot-Py")
