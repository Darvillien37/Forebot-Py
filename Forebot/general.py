from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot, logger):
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
        self.logger.error(f'{ctx.author} sent [{ctx.message.content}]\
 resulting in: [{error}]')
        print(error)
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this \
                command.')
