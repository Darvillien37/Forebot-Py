from discord.ext import tasks, commands


class StartUpLoops(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.log_reset_first_loop = True
        self.log_reset.start()

    def cog_unload(self):
        self.log_reset.cancel()

    @tasks.loop(seconds=60, count=2)
    async def log_reset(self):
        if (self.log_reset_first_loop is True):
            self.log_reset_first_loop = False
        else:
            self.logger.info("Start-up loops: Setting logger to INFO mode.")
            self.logger.setLevel("INFO")

    @log_reset.before_loop
    async def before_log_resetter(self):
        self.logger.info("Start-up loops: Waiting until bot is ready.")
        await self.bot.wait_until_ready()
