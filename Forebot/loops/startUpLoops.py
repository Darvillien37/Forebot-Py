from discord.ext import tasks, commands


class StartUpLoops(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.log_resetter_first_loop = True
        self.log_resetter.start()

    def cog_unload(self):
        self.log_resetter.cancel()

    @tasks.loop(seconds=60, count=2)
    async def log_resetter(self):
        if(self.log_resetter_first_loop is True):
            self.log_resetter_first_loop = False
        else:
            self.logger.info("Start-up loops: Setting logger to INFO mode.")
            self.logger.setLevel("INFO")

    @log_resetter.before_loop
    async def before_log_resetter(self):
        self.logger.info("Start-up loops: Waiting until bot is ready.")
        await self.bot.wait_until_ready()
