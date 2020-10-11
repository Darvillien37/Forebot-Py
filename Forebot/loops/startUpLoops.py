from discord.ext import tasks, commands
import time


class StartUpLoops(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=1, count=1)
    async def printer(self):
        time.sleep(60)
        self.logger.info("Start-up loops: Setting logger to INFO mode.")
        self.logger.setLevel("INFO")

    @printer.before_loop
    async def before_printer(self):
        self.logger.info("Start-up loops: Waiting until bot is ready.")
        await self.bot.wait_until_ready()
