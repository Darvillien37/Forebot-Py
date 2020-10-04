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
        self.logger.info(f'{ctx.author} Triggered message purge ({amount})'
                         f' [{ctx.guild.name}: {ctx.channel.name}]')
        # To delete the message asked for as well
        amount = amount + 1
        await ctx.channel.purge(limit=amount)

    @commands.command(help='Kick a member from the server')
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, member: discord.Member, *, reason='No Reason'):
        self.logger.info(f'{ctx.author} Kicked {member.name} From '
                         f'{ctx.guild.name} for [{reason}]')
        # kick the member
        await member.kick(reason=reason)

    @commands.command(help='Ban a member from the server')
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, member: discord.Member, *, reason='No Reason'):
        self.logger.info(f'{ctx.author} BANNED {member.name} From '
                         f'{ctx.guild.name} for [{reason}]')
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

        self.logger.info(f'{ctx.author} UNBANNED {mem_name} From '
                         f'{ctx.guild.name}')

    @commands.command(aliases=['getWarn'],
                      help='Get the guild warnings for a member')
    @commands.has_permissions(administrator=True)
    async def getWarnings(self, ctx, member: discord.Member):
        self.logger.info(f'{ctx.author} Getting warnings for {member.name}'
                         f' From {ctx.guild.name}')

        warnings = Users.get_warnings(member.id, ctx.guild.id)

        embedVar = discord.Embed(title=f"({len(warnings)}) Warnings for"
                                 f"{member.name}", color=0xff0000)
        for warn in warnings:
            embedVar.add_field(name=f"{warn['id']} - {warn['dateTime']}",
                               value=warn['warning'],
                               inline=False)

        await ctx.send(embed=embedVar)

    @commands.command(aliases=['warn'])
    async def addWarning(self, ctx, member: discord.Member, *, warning: str):
        Users.add_warning(member.id, ctx.guild.id, warning)
        await ctx.send(f"You {member.mention} have been warnned!!")
        await self.getWarnings(ctx, member)

    @commands.command(aliases=['remWarn', 'rWarn'])
    async def removeWarning(self, ctx, member: discord.Member, id: int):
        self.logger.info(f'{ctx.author} Removing warning {id} for '
                         f'{member.name}')
        removed = Users.remove_warning(member.id, id)
        if removed:
            await ctx.send("Warning removed")
        else:
            await ctx.send("Warning ID not found")
