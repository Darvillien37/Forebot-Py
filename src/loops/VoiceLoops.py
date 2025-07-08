from discord.ext import tasks, commands
from Database import Database
from datetime import datetime, timedelta, timezone
import XP
from Utils import utils


class VoiceXPLoop(commands.Cog):
    def __init__(self, bot: commands.Bot, logger):
        self.bot: commands.Bot = bot
        self.logger = logger
        self.loop_counter = 0

    def cog_unload(self):
        if self.voice_xp_loop.is_running():
            self.voice_xp_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.voice_xp_loop.is_running():
            self.voice_xp_loop.start()

    @tasks.loop(minutes=5)
    async def voice_xp_loop(self):
        self.loop_counter += 1
        if (self.loop_counter % 5) == 0:  # every half hour
            self.logger.info(f"Voice loop: Running {self.loop_counter} times.")

        for guild in self.bot.guilds:
            for vc in guild.voice_channels:
                members = [m for m in vc.members if not m.bot
                           and not m.voice.self_mute
                           and not m.voice.self_deaf
                           and not m.voice.deaf  # server deafened
                           and not m.voice.mute  # server muted
                           and not m.voice.afk  # in AFK channel
                           ]

                if len(members) < 2:
                    continue  # Anti-AFK: at least 2 active human users

                for member in members:
                    last_ts = Database.get_last_voice_xp(member.id)
                    # if for some reason the user missed the VC join event, update it now
                    if last_ts is None:
                        Database.update_last_voice_xp(member.id)
                        continue
                    now = datetime.now(timezone.utc)

                    if not last_ts or (now - last_ts >= timedelta(minutes=10)):
                        # Give XP
                        self.logger.info(f"Voice loop: Awarding XP to {member.display_name}.")

                        chan = utils.find_default_channel(guild.me, guild)
                        await XP.give_from_values(3, 10, member, chan, "From Voice Activity!")
                        Database.update_last_voice_xp(member.id)

    @voice_xp_loop.before_loop
    async def before_loop(self):
        self.logger.info("Voice loop: Waiting until bot is ready.")
        await self.bot.wait_until_ready()
