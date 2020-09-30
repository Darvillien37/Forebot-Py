from discord.ext import commands
import discord
from Storage import Users


class Admin(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    @commands.command(help='Clear an amount of messages')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=5):
        msg = f'{ctx.author} Triggered message purge ({amount})'\
              f' [{ctx.guild.name}: {ctx.channel.name}]'
        print(msg)
        self.logger.info(msg)
        # To delete the message asked for as well
        amount = amount + 1
        await ctx.channel.purge(limit=amount)

    @commands.command(help='Kick a member from the server')
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, member: discord.Member, *, reason='No Reason'):
        msg = f'{ctx.author} Kicked {member.name} From {ctx.guild.name}'\
              f' for [{reason}]'
        print(msg)
        self.logger.info(msg)
        # kick the member
        await member.kick(reason=reason)

    @commands.command(help='Ban a member from the server')
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, member: discord.Member, *, reason='No Reason'):
        msg = f'{ctx.author} BANNED {member.name} From {ctx.guild.name}'\
              f' for [{reason}]'
        print(msg)
        self.logger.info(msg)
        # Ban the member
        await member.ban(reason=reason)

    @commands.command(help='Unban a member from the server')
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, member):
        # get the list of all bans
        banned_users = await ctx.guild.bans()
        # split the member around the # to get the name and number
        if '#' in member:
            mem_name, mem_disc = member.split('#')
        else:
            mem_name = member

        for ban_entry in banned_users:
            user = ban_entry.user

            if user.name == mem_name:
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                break

        msg = f'{ctx.author} UNBANNED {mem_name} From {ctx.guild.name}'
        print(msg)
        self.logger.info(msg)

    @commands.command(help='Ban a member from the server')
    @commands.has_permissions(administrator=True)
    async def getWarnings(self, ctx, member: discord.Member):
        msg = f'{ctx.author} Getting warnings for {member.name}'\
              f' From {ctx.guild.name}'
        print(msg)
        self.logger.info(msg)
        Users.get_warnings(member.id, ctx.guild.id)
