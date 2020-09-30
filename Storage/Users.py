from os import path
import json
from . import XP


def user_exists(users, user_id: str):
    '''
    Checks if the user exists, and if not creates it.
    '''
    if user_id not in users:
        users[user_id] = {}
        users[user_id]['experience'] = 0
        users[user_id]['level'] = 0


def GiveXP(userID: str, xpAmount):
    '''
    Give XP to a user.
    Keyword arguments:
    userID -- the users id to give xp to.
    xpAmount -- the amount of xp to give to the user.
    Returns:
    leveledUp -- If the user leveled up.
    userLevel -- The level of the user.
    '''
    # ToDo: Claim Lock here
    # variable to return, assume false
    leveledUp = False
    dataFile = path.join(path.dirname(__file__), 'Data/Users.json')

    with open(dataFile, 'r') as f:
        users = json.load(f)

    # check if the user exists, if not add them
    user_exists(users, userID)

    # get the users level data.
    userXP = users[userID]['experience']
    userLevel = users[userID]['level']

    # add their xp earned.
    userXP = userXP + xpAmount

    # now check if they've leveld up
    xpToLvlUp = XP.calculate_xp_for_next_level(userLevel)

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
