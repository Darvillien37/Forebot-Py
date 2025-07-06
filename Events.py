import traceback
import discord
from Database import Database
from Lootboxes.ClaimView import ClaimNowButton
import XP
from discord.ext import commands


class Events(commands.Cog):
    '''
    A Cog class for general discord bot event listeners
    '''
    def __init__(self, bot, logger):
        '''
        Constructor for the Cog General class.
        Keyword arguments:
        bot -- discord bot object.
        logger -- the logger to log to.
        '''
        self.bot = bot
        self.logger = logger

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()  # Sync the slash commands with Discord
        print(f'{self.bot.user} has connected to Discord!')
        print('Connected to guilds:')
        for guild in self.bot.guilds:
            print(f'\t-{guild.name}(id: {guild.id})')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Get traceback info
        tb_lines = traceback.format_exception(type(error), error, error.__traceback__)
        tb_text = ''.join(tb_lines)
        msg = f'{ctx.author} sent [{ctx.message.content}] with error:\n [{tb_text}]'
        self.logger.error(msg)

        if isinstance(error, commands.errors.CommandNotFound):
            return
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this command.')
            return
        if isinstance(error, commands.errors.CommandError):
            await ctx.send(f"Something's not right there buddy! Try typing:"
                           f"```'{self.bot.command_prefix}help {ctx.command.name}'```")
            return

    @commands.Cog.listener()
    async def on_message(self, message):
        # if the message is from this bot, ignore it.
        if message.author == self.bot.user:
            return
        if message.author.bot:
            return

        await self.__do_xp_give(message.content,
                                message.author,
                                message.channel)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # if the message is from this bot, ignore it.
        if payload.user_id == self.bot.user.id:
            return
        # Substitute the message id + user id for the message content
        await self.__do_xp_give(str(payload.message_id) + str(payload.user_id),
                                payload.member,
                                self.bot.get_channel(payload.channel_id))

    async def __do_xp_give(self, msg_content, author, channel):
        # Get the amount of xp gained for the message
        xp_gained = XP.get_xp_from_message(msg_content)
        user = Database.get_user(author.id)
        # print(user)
        user_id, xp, level, coins = user
        xp += xp_gained

        threshold = XP.get_xp_threshold(level)
        if xp >= threshold:
            xp -= threshold
            level += 1
            tier = Database.roll_loot_tier()
            Database.add_lootbox(user_id, tier)
            color = discord.Color(Database.LOOT_TIERS[tier]["color"])
            embed = discord.Embed(
                title="🆙 Level Up!",
                description=(
                    f"{author.mention} reached **Level {level}**!\n"
                    f"🎁 You've earned a **{tier.title().upper()} Lootbox**!"
                ),
                color=color
            )
            message = await channel.send(embed=embed)
            claimBtn = ClaimNowButton(user_id, tier, message)
            await message.edit(view=claimBtn)

        Database.update_user(user_id, xp, level, coins)
