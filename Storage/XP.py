from random import randint
import json
from os import path


def GetXPFromMessage(message: str):
    # the smallest maximum amount
    minMax = int(len(message) / 3)
    if minMax < 3:
        minMax = 3
    amount = randint(1, minMax)
    return amount


def GiveXP(userID: str, xpAmount):
    # ToDo: Claim Lock here
    # variable to return, assume false
    leveledUp = False
    dataFile = path.join(path.dirname(__file__), 'Data/XP.json')

    with open(dataFile, 'r') as f:
        users = json.load(f)

    # check if the user exists, if not add them
    __user_exists(users, userID)

    # get the users level data.
    userXP = users[userID]['experience']
    userLevel = users[userID]['level']

    # add their xp earned.
    userXP = userXP + xpAmount

    # now check if they've leveld up
    xpToLvlUp = __calculate_xp_for_next_level(userLevel)

    # If the user's xp is above the threshold for their current level
    # then they have leveled up.
    if (userXP >= xpToLvlUp):
        # Remove that xp threshold
        userXP = userXP - xpToLvlUp
        # and level them up
        userLevel = userLevel + 1
        leveledUp = True

    # Update the user's data.
    users[userID]['experience'] = int(userXP)
    users[userID]['level'] = int(userLevel)

    with open(dataFile, 'w') as f:
        json.dump(users, f, indent=4)

    # ToDo: Release Lock here
    return (leveledUp, userLevel)


def __calculate_xp_for_next_level(currLvl):
    return pow(currLvl, 1.5) + 25


def __user_exists(users, userID):
    if userID not in users:
        users[userID] = {}
        users[userID]['experience'] = 0
        users[userID]['level'] = 0
