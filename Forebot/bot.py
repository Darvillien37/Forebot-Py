import logging

from discord.ext import commands

from .general import General
from .commands.greetings import Greetings
from .commands.fun import Fun


class Bot():
    def __init__(self, prefix, tkn):
        self.bot = commands.Bot(command_prefix=prefix)
        self.token = tkn

        self.bot.add_cog(General(self.bot))
        self.bot.add_cog(Greetings(self.bot))
        self.bot.add_cog(Fun(self.bot))

    def get_logger(self):
        return logging.getLogger('discord')

    def run(self):
        """
        docstring
        """
        self.bot.run(self.token)
