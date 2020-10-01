from discord.ext import commands


class Other(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    @commands.command(help='Check the progress of Forebots development')
    async def trello(self, ctx):
        await ctx.message.delete()
        await ctx.send("Link to the Forebot trello board:"
                       " https://trello.com/b/GO9a8ZAd")
