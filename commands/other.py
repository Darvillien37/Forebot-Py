from Database import Database
from Lootboxes.ClaimView import LootboxClaimView
import XP
from discord.ext import commands
import discord


class Other(commands.Cog):
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

    @commands.hybrid_command(aliases=['info'], help='Get info about a user, or yourself')
    async def user_info(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        self.logger.info(f'{ctx.author.name} getting info for: {member.name}')

        user = Database.get_user(member.id)
        user_id, xp, level, coins = user
        threshold = XP.get_xp_threshold(level)
        myEmbed = discord.Embed(title=f"{member.name}'s info:", color=discord.Color.gold())
        myEmbed.set_thumbnail(url=member.avatar.url)
        myEmbed.add_field(name="XP",        value=f"{xp}/{threshold}", inline=True)
        myEmbed.add_field(name="Level",     value=f"{level}", inline=True)
        myEmbed.add_field(name="💰Coins",  value=f"{coins}", inline=True)

        await ctx.send(embed=myEmbed)

    @commands.hybrid_command(aliases=['lootbox', 'boxes'], help="View and Claim your lootboxes.")
    async def lootboxes(self, ctx):
        user = ctx.author
        self.logger.info(f'{ctx.author.name} getting Lootboxes for: {user.name}')
        boxes = Database.get_lootboxes(user.id)
        if not boxes:
            await ctx.send("User not found.")
            return

        embed = discord.Embed(
            title=f"{user.display_name}'s Lootboxes",
            color=discord.Color.blurple()
        )
        for (tier, count) in zip(Database.LOOT_TIERS.keys(), boxes):
            emoji = Database.LOOT_TIERS[tier]["emoji"]
            embed.add_field(name=f"{emoji} {tier.title()}", value=str(count), inline=True)

        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        view = LootboxClaimView(user.id)
        
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(help="Open your best available lootbox!")
    async def claim(self, ctx):
        result = Database.claim_lootbox(ctx.author.id)
        if result is None:
            await ctx.send("❌ You don't have any lootboxes to claim.")
            return

        tier, reward = result
        color = discord.Color(Database.LOOT_TIERS[tier]["color"])
        embed = discord.Embed(
            title=f"{tier.title()} Lootbox Opened!",
            description=f"You received **💰 {reward} coins**!",
            color=color
        )
        await ctx.send(embed=embed)

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

