import os
from dotenv import load_dotenv
from Forebot.bot import Bot
import logging

# Load the enviroment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

fbot = Bot(os.getenv("PREFIX"), TOKEN)

logger = fbot.get_logger()
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="log.log", encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: \
    %(message)s'))
logger.addHandler(handler)
fbot.run()
