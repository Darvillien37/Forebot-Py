import os
import random

import discord
from dotenv import load_dotenv
from discord.ext import commands

#Load the enviroment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix=os.getenv("PREFIX"))

@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    responce = random.choice(brooklyn_99_quotes)
    await ctx.send(responce)

@bot.command(name='roll', help='Roll some dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(','.join(dice))

@bot.command(name='create-channel')
@commands.has_role('Admin')
async def create_channel(ctx, channel_name='real-python'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating new Channel: {channel_name}')
        await guild.create_text_channel(channel_name)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('Connected to guilds:')
    for guild in bot.guilds:
        print(f'\t-{guild.name}(id: {guild.id})')


@bot.event
async def on_member_join(member):
    sys_chan = member.guild.system_channel
    if (sys_chan is not None):
        await member.guild.system_channel.send(f'It\'s Ya Boi, {member.mention}')


bot.run(TOKEN)
