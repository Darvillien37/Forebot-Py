import discord
from random import randint
from Database import Database, Items
from views.ClaimNowButton import ClaimNowButton


def __get_xp_from_message(message: str):
    '''
    Get an amount of XP based off a message string
    '''
    # the smallest maximum amount
    minMax = int(len(message) / 3)
    if minMax < 3:
        minMax = 3
    amount = randint(1, minMax)
    return amount


def get_xp_threshold(currLvl, ret_float: bool = False):
    a = 3
    b = 2
    c = 100
    if ret_float:
        return (a * pow(currLvl, b)) + c
    else:
        return int((a * pow(currLvl, b)) + c)


async def give_from_msg(msg_content: str, user: discord.Member, announce_channel: discord.TextChannel, reason: str = None):
    # Get the amount of xp gained for the message
    xp_gained = __get_xp_from_message(msg_content)
    await __give_xp(xp_gained, user, announce_channel, reason)
    return xp_gained


async def give_from_values(min: int, max: int, user: discord.Member, announce_channel: discord.TextChannel, reason: str = None):
    # error check to make sure min not less than max
    if min > max:
        min = max
    xp_gained = randint(min, max)
    await __give_xp(xp_gained, user, announce_channel, reason)
    return xp_gained


async def __give_xp(xp_amount: int, user: discord.Member, announce_channel: discord.TextChannel, reason: str = None):
    (xp, level) = Database.get_user_xp_level(user.id)
    xp += xp_amount
    threshold = get_xp_threshold(level)

    # Check for level up
    if xp >= threshold:
        xp -= threshold
        level += 1
        tier = Database.roll_loot_tier()
        Database.add_lootbox(user.id, tier)
        color = discord.Color(Items.LOOT_TIERS[tier]["color"])
        embed = discord.Embed(
            title="🆙 Level Up!",
            description=(
                f"{user.mention} reached **Level {level}**!\n"
                f"{reason if reason else ''}\n"
                f"🎁 You've earned a **{tier.title().upper()} Lootbox**!"
            ),
            color=color
        )
        message = await announce_channel.send(embed=embed)
        claimBtn = ClaimNowButton(user.id, tier, message)
        await message.edit(view=claimBtn)

    Database.set_user_xp_level(user.id, xp, level)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    # Generate x values (non-negative because of x^1.5)
    x = np.linspace(0, 50, 400)
    y = get_xp_threshold(x, True)

    # Plot
    plt.figure(figsize=(8, 5))
    plt.plot(x, y, color='blue')
    plt.xlabel('Level')
    plt.ylabel('XP')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
