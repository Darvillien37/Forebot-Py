from Database import Database, attributes
import XP
from discord.ext import commands
import discord

from views.AttributeUpgradeView import AttributeUpgradeView


class User(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    # @commands.command(help='Check the progress of Forebots development')
    # async def trello(self, ctx):
    #     self.logger.info(f'{ctx.author.name} triggered \'trello\' command')
    #     await ctx.message.delete()
    #     await ctx.send("Link to the Forebot trello board:"
    #                    " https://trello.com/b/GO9a8ZAd")

    # @commands.command(help='Link to 4bot source code')
    # async def github(self, ctx):
    #     self.logger.info(f'{ctx.author.name} triggered \'github\' command')
    #     await ctx.message.delete()
    #     await ctx.send("Link to the Forebot github:"
    #                    " https://github.com/Darvillien37/Forebot-Py")

    @commands.hybrid_command(help='Get info about a user, or yourself')
    async def info(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        user = Database.get_user(member.id)
        user_id, xp, level, coins = user
        threshold = XP.get_xp_threshold(level)
        myEmbed = discord.Embed(title=f"{member.display_name}'s info:", color=discord.Color.gold())
        myEmbed.set_thumbnail(url=member.avatar.url)
        myEmbed.add_field(name="XP",        value=f"{xp}/{threshold}", inline=True)
        myEmbed.add_field(name="Level",     value=f"{level}", inline=True)
        myEmbed.add_field(name="ForeCoins", value=f"{coins}", inline=True)

        await ctx.send(embed=myEmbed)

    @commands.hybrid_command(aliases=['stats'])
    @discord.app_commands.describe(show_tips="Whether to show attribute descriptions")
    async def attributes(self, ctx: commands.Context, show_tips: bool = False):
        user_id = ctx.author.id
        attr_data = Database.get_user_attributes(user_id)

        embed = attributes.build_attribute_embed(ctx.author, attr_data, show_tips)
        view = None
        message = await ctx.send(embed=embed, view=view)

        if attr_data['unspent_points'] > 0:
            view = AttributeUpgradeView(bot=self.bot,
                                        member=ctx.author,
                                        attr_dict=attr_data,
                                        original_embed=embed,
                                        original_message=message,
                                        show_tips=show_tips)
        await message.edit(view=view)

    # @commands.command(aliases=['tt'], help='Get the top 10 people in the guild')
    # async def topTen(self, ctx):
    #     self.logger.info(f'{ctx.author.name} getting Top 10 for: {ctx.guild.name}')
    #     # Get the top 10 users
    #     top_ten = Users.top_ten(ctx.guild.id)

    #     # Create an embed
    #     myEmbed = discord.Embed(title=f"{ctx.guild.name} Top Ten Members", color=0x0000ff)
    #     myEmbed.set_thumbnail(url=ctx.guild.icon_url)

    #     # Create a field for all the users
    #     for user in top_ten:
    #         member = ctx.guild.get_member(int(user['ID']))
    #         if member is None:
    #             continue
    #         # prefer guild nicknames
    #         if member.nick is None:
    #             name = member.name
    #         else:
    #             name = member.nick

    #         myEmbed.add_field(name=name,
    #                           value=f"Lvl: {user['level']}\n"
    #                                 f"Exp: {user['experience']}",
    #                           inline=True)

    #     await ctx.send(embed=myEmbed)
