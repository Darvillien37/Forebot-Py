from Database import Database, attributes
import XP
from discord.ext import commands
import discord

from views.AttributeUpgradeView import AttributeUpgradeView


class User(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.medals = ["🥇", "🥈", "🥉"]

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

    @commands.hybrid_command(aliases=['stats'], help="View and assign your attributes.")
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

    @commands.hybrid_command(name="topten", help="View the top 10 people in this guild.")
    @discord.app_commands.describe(global_leaderboard="Whether to show the Global top 10, and not just this guild.")
    async def top_ten(self, ctx: commands.Context, global_leaderboard: bool = False):
        ids = None
        title = "🌍 Global Top 10"
        embed_thumb = None
        if global_leaderboard is False:
            if ctx.guild.icon is not None:
                embed_thumb = ctx.guild.icon.url
            title = f"🏆 Top 10 in {ctx.guild.name}"
            ids = []
            for member in ctx.guild.members:
                ids.append(str(member.id))

        user_data = Database.get_users_ordered(ids)
        embed = discord.Embed(title=title, color=discord.Color.blurple())
        embed.set_thumbnail(url=embed_thumb)
        if not user_data:
            embed.description = "No users found!"
        else:

            for i, (user_id, xp, level, coins) in enumerate(user_data, start=1):
                emoji = self.medals[i - 1] if i <= len(self.medals) else f"#{i}"
                user = self.bot.get_user(user_id)
                name = user.display_name if user else f"<@{user_id}>"
                embed.add_field(
                    name=f"{emoji} - {name}",
                    value=f"Level {level} • {xp} XP\nCoins {coins}",
                    inline=True
                )
                if i >= 10:
                    break
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rank", description="Shows your current ranking.")
    @discord.app_commands.describe(show_global="Check your global rank.")
    @discord.app_commands.describe(member="The member to check the rank of.")
    async def rank(self,  ctx: commands.Context, member: discord.Member = None, show_global: bool = False):
        if member:
            user = member
        else:
            user = ctx.author
        ids = None
        title = f"🌍 {user.display_name}'s Global Rank"
        embed_thumb = None
        if show_global is False:
            if ctx.guild.icon is not None:
                embed_thumb = ctx.guild.icon.url
            title = f"📊 {user.display_name}'s Rank in {ctx.guild.name}"
            ids = []
            for member in ctx.guild.members:
                ids.append(str(member.id))

        user_data = Database.get_users_ordered(ids)
        rank = None
        xp = 0
        level = 0
        emoji = ""
        for i, (uid, uxp, ulevel, _) in enumerate(user_data, start=1):
            if user.id == uid:
                emoji = self.medals[i - 1] if i <= len(self.medals) else ""
                rank = i
                xp = uxp
                level = ulevel
                break

        if rank is None:
            desc = "You haven't earned any XP yet!"
        else:
            desc = f"You're ranked {emoji}**#{rank}**{emoji} — Level **{level}** • **{xp}** XP."

        embed = discord.Embed(title=title, description=desc, color=discord.Color.blue())
        embed.set_thumbnail(url=embed_thumb)
        await ctx.send(embed=embed)
