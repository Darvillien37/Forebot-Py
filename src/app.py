import asyncio
from datetime import datetime
from discord.ext import commands
import os
import logging
import json
import discord
import Database.Database as Database
from commands.Economy import Economy
# from loops.startUpLoops import StartUpLoops
from Events import Events
from commands.greetings import Greetings
from Lootboxes.Lootboxes import Lootboxes
from commands.fun import Fun
from commands.admin import Admin
# from commands.owner import Owner
from commands.other import Other
from commands.EasterEggs import EasterEggs
from loops.VoiceLoops import VoiceXPLoop


# ------------------ CONFIG ------------------
CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    "token": "TOKEN_HERE",
    "resource_path": "./resources",
    "db_file": "./bot_data.db",
    "log_path": "./logs/",
    "prefix": ";"
}

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)
    print(f"Config file '{CONFIG_FILE}' created. Please fill in the values and restart the bot.")
    exit(1)

with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)

TOKEN = os.path.normpath(config["token"])
RESOURCE_PATH = os.path.abspath(os.path.normpath(config['resource_path']))
DB_FILE = os.path.abspath(os.path.normpath(config['db_file']))
PREFIX = config['prefix']
LOG_PATH = os.path.abspath(os.path.normpath(config['log_path']))
if not os.path.exists(LOG_PATH):
    print(f"Log Path doesn't exist: {LOG_PATH}")
    exit(1)
if not os.path.exists(RESOURCE_PATH):
    print(f"Resource Path doesn't exist: {LOG_PATH}")
    exit(1)


# ------------------ LOGGER ------------------
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# now_str = "now"


handler = logging.FileHandler(filename=f"{LOG_PATH}/forebot_{now_str}.log", encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


# ------------------ DATABASE ------------------
Database.init_db(DB_FILE)
# Database.dt_testing()
# exit(0)

# ------------------ BOT SETUP ------------------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True
bot = commands.Bot(command_prefix=PREFIX, case_insensitive=True, intents=intents)


async def setup():
    # await bot.add_cog(StartUpLoops(bot, logger))
    await bot.add_cog(Events(bot, logger))
    await bot.add_cog(Greetings(bot, logger))
    await bot.add_cog(Economy(bot, logger))
    await bot.add_cog(Fun(bot, RESOURCE_PATH, logger))
    await bot.add_cog(Lootboxes(bot, logger))
    await bot.add_cog(VoiceXPLoop(bot, logger))

    await bot.add_cog(Admin(bot, logger))
    # await bot.add_cog(Owner(bot, logger))
    await bot.add_cog(Other(bot, logger))
    await bot.add_cog(EasterEggs(bot, logger))

asyncio.run(setup())
bot.run(TOKEN)
