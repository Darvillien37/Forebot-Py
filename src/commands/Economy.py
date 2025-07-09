from discord.ext import commands
import discord
from Database import Database


class Economy(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    @commands.hybrid_command(name="give", help="Give coins to another user.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def give(self, ctx: commands.Context, member: discord.Member, amount: int):
        if member.id == ctx.author.id:
            await ctx.send("❌ You can't give coins to yourself.")
            return
        if amount <= 0:
            await ctx.send("❌ The amount must be greater than zero.")
            return

        giver = Database.get_user(ctx.author.id)
        receiver = Database.get_user(member.id)

        if giver is None or receiver is None:
            await ctx.send("❌ User data not found.")
            return

        _, _, _, coins = giver

        if coins < amount:
            await ctx.send("❌ You don't have enough coins to give.")
            return

        # Update both users
        Database.update_coins(ctx.author.id, -amount)
        Database.update_coins(member.id, amount)

        await ctx.send(f"✅ {ctx.author.mention} gave **{amount} coins** to {member.mention}!")
