from discord.ext import commands
from Storage import Users, XP


class General(commands.Cog):
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
        print(f'{self.bot.user} has connected to Discord!')
        print('Connected to guilds:')
        for guild in self.bot.guilds:
            print(f'\t-{guild.name}(id: {guild.id})')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        msg = f'{ctx.author} sent [{ctx.message.content}] with error [{error}]'
        self.logger.error(msg)
        print(msg)
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this '
                           'command.')
        if isinstance(error, commands.errors.CommandError):
            await ctx.send(f"Somthing's not right there buddy! Try typing:"
                           f"```'{self.bot.command_prefix}help "
                           f"{ctx.command.name}'```")

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
        xp = XP.getXPFromMessage(msg_content)
        leveledUp, newLevel = Users.GiveXP(str(author.id), xp)

        # If the user leveled up, let them know and congratulate them
        if(leveledUp):
            await channel.send(f'Congratulations!!'
                               f' {author.mention}'
                               f' leveled up to lvl: {newLevel}')
