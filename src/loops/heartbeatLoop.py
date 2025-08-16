from logging import Logger
from discord.ext import tasks, commands
from Database import Database


class HeartbeatLoop(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: Logger):
        self.bot: commands.Bot = bot
        self.logger = logger
        self.first_loop = True
        self.bot_connected = False

    def cog_unload(self):
        if self.update_heartbeat.is_running():
            self.update_heartbeat.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.update_heartbeat.is_running():
            self.update_heartbeat.start()

    @commands.Cog.listener()
    async def on_connect(self):
        self.bot_connected = True

    @commands.Cog.listener()
    async def on_resumed(self):
        self.bot_connected = True

    @commands.Cog.listener()
    async def on_disconnect(self):
        self.bot_connected = False

    @tasks.loop(minutes=60)
    async def update_heartbeat(self):
        if (self.bot_connected):
            if self.first_loop:
                self.first_loop = False
            else:
                self.logger.info("Updating Heartbeat Timestamp")
                Database.update_heartbeat_timestamp()
        else:
            self.logger.info("Bot not connected")

    @update_heartbeat.before_loop
    async def before_update_heartbeat(self):
        await self.bot.wait_until_ready()
