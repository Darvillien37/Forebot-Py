from discord.ext import commands
from Storage import XP


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
        msg = f'{ctx.author} sent [{ctx.message.content}] with error [{error}]'
        self.logger.error(msg)
        print(msg)
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this '
                           'command.')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        xp = XP.GetXPFromMessage(message.content)

        leveledUp, newLevel = XP.GiveXP(str(message.author.id), xp)

        if(leveledUp):
            await message.channel.send(f'Congratulations!!'
                                       f' {message.author.mention}'
                                       f' leveled up to lvl: {newLevel}')
