from discord.ext import tasks, commands
from Storage import Users
from datetime import datetime


class WarningLoops(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.expired_warning_timeout.start()

    def cog_unload(self):
        self.expired_warning_timeout.cancel()

    @tasks.loop(hours=1)
    async def expired_warning_timeout(self):
        now = datetime.now()
        # if it is 1AM check the warnings
        if now.hour == 1:
            self.logger.info("Clearing expired warnings")
            Users.clear_expired_warnings()
