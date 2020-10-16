import os
from dotenv import load_dotenv
from Forebot.bot import Bot
import logging
from Storage import Users
# Load the environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
RESOURCE_FOLDER = os.getenv("RESOURCE_FOLDER")

# Initialise the bot
fBot = Bot(os.getenv("PREFIX"), TOKEN, RESOURCE_FOLDER)

# force update the users to ensure they have all the keys
Users.force_update_users()


# Create the logger for the bot
logger = fBot.get_logger()
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="log.log", encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: \
    %(message)s'))
logger.addHandler(handler)

fBot.run()
