import logging
from discord.ext import commands
from .general import General
from .commands.greetings import Greetings
from .commands.fun import Fun
from .commands.admin import Admin
from .commands.owner import Owner
from .commands.other import Other


class Bot():
    def __init__(self, prefix, tkn, res):
        self.bot = commands.Bot(command_prefix=prefix, case_insensitive=True)
        self.token = tkn
        self.resourceDirectory = res

        self.bot.add_cog(General(self.bot, self.get_logger()))
        self.bot.add_cog(Greetings(self.bot))
        self.bot.add_cog(Fun(self.bot, self.resourceDirectory))
        self.bot.add_cog(Admin(self.bot, self.get_logger()))
        self.bot.add_cog(Owner(self.bot, self.get_logger()))
        self.bot.add_cog(Other(self.bot, self.get_logger()))

    def get_logger(self):
        return logging.getLogger('discord')

    def run(self):
        """
        docstring
        """
        self.bot.run(self.token)
