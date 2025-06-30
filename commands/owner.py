import logging
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    @commands.command(help='change the logging level [crit, err, warn, info,'
                      ' debug]')
    @commands.is_owner()
    async def logLevel(self, ctx, level: str):
        level = level.upper()

        if level == 'CRIT':
            self.logger.critical('Setting log level [CRITICAL]')
            self.logger.setLevel(logging.CRITICAL)
            await ctx.send('Log level changed to [CRITICAL]')

        elif level == 'ERR':
            self.logger.error('Setting log level [ERROR]')
            self.logger.setLevel(logging.ERROR)
            await ctx.send('Log level changed to [ERROR]')

        elif level == 'WARN':
            self.logger.warning('Setting log level [WARNING]')
            self.logger.setLevel(logging.WARNING)
            await ctx.send('Log level changed to [WARNING]')

        elif level == 'INFO':
            self.logger.info('Setting log level [INFO]')
            self.logger.setLevel(logging.INFO)
            await ctx.send('Log level changed to [INFO]')

        elif level == 'DEBUG':
            self.logger.info('Setting log level [DEBUG]')
            self.logger.setLevel(logging.DEBUG)
            await ctx.send('Log level changed to [DEBUG]')

        else:
            await ctx.send(f'unknown[{level}] try [crit, err, warn, info,'
                           'debug]')
