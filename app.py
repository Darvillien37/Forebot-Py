import os

import discord
from dotenv import load_dotenv
import random

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print('Connected to guilds:')
    for guild in client.guilds:
        print(f'\t-{guild.name}(id: {guild.id})')


@client.event
async def on_member_join(member):
    await member.create_dm()
    #await member.dm_channel.send(f'Hi {member.name}, welcome to my Discord server!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    if message.content == '99!':
        response = random.choice(brooklyn_99_quotes)
        await message.channel.send(response)



client.run(TOKEN)