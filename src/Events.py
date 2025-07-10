import traceback
from discord.ext import commands
import XP
from Database import Database


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
        print("\nUsers in Database:")
        user_ids = Database.get_all_user_ids()
        for user_id in user_ids:
            user = self.bot.get_user(user_id[0])
            if user is not None:
                print(f"{user.display_name} : {user.id}")
            else:
                print(f"Unknown User: {user_id[0]}")

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

        await XP.give_from_msg(message.content,
                               message.author,
                               message.channel)

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        args = " ".join(f"{k}={v}" for k, v in ctx.kwargs.items())
        self.logger.info(f'{ctx.author.display_name} called command [{ctx.command.qualified_name} {args}]')

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        # if the message is from a bot, ignore it.
        if ctx.author.bot:
            return
        xp_gained = await XP.give_from_values(1, 5, ctx.author, ctx.channel)
        self.logger.info(f"{ctx.author.display_name} was awarded {xp_gained} xp for [{ctx.command.qualified_name}]")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # if the message is from this bot, ignore it.
        if payload.user_id == self.bot.user.id:
            return
        # Substitute the message id + user id for the message content
        xp_gained = await XP.give_from_msg(str(payload.message_id) + str(payload.user_id),
                                           payload.member,
                                           self.bot.get_channel(payload.channel_id))
        self.logger.info(f"{payload.member.display_name} was awarded {xp_gained} xp for Reacting")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Joined voice
        if not before.channel and after.channel:
            print(f"{member.name} Joined {after.channel.name}")
            Database.update_last_voice_xp(member.id)
        # Left voice
        elif before.channel and not after.channel:
            print(f"{member.name} Left {before.channel.name}")
            Database.clear_last_voice_xp(member.id)
        # Switched voice channel
        elif before.channel != after.channel:
            print(f"{member.name} Moved from {before.channel.name} to {after.channel.name}")
