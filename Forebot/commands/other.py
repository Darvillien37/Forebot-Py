from discord.ext import commands
import discord
from Storage import Users


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

    @commands.command(help='Link to 4bot source code')
    async def github(self, ctx):
        self.logger.info(f'{ctx.author.name} triggered \'github\' command')
        await ctx.message.delete()
        await ctx.send("Link to the Forebot github:"
                       " https://github.com/Darvillien37/Forebot-Py")

    @commands.command(aliases=['info'], help='Get info about a user, or youself')
    async def userInfo(self, ctx, member: discord.Member = None):
        if(member is None):
            member = ctx.author
        self.logger.info(f'{ctx.author.name} getting info for: {member.name}')
        uInfo = Users.get_info(member.id, ctx.guild.id)
        myEmbed = discord.Embed(title=f"{member.name}'s info:", color=0x0000ff)
        myEmbed.set_thumbnail(url=member.avatar_url)
        for line in uInfo:
            sLine = line.split(':')
            myEmbed.add_field(name=sLine[0], value=sLine[1], inline=True)
        await ctx.send(embed=myEmbed)
