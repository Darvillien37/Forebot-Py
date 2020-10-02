from os import path
import json
from . import XP
from datetime import datetime


def user_exists(users, user_id: str):
    '''
    Checks if the user exists, and if not creates it.
    Returns true if the user already existed, false if they had to be created
    '''
    if user_id not in users:
        users[user_id] = {}
        users[user_id]['experience'] = 0
        users[user_id]['level'] = 0
        users[user_id]['warnings'] = []
        return False
    if 'warnings' not in users[user_id]:
        users[user_id]['warnings'] = []
        return False
    return True


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


def get_warnings(userID, guildId):
    '''
    Get the warnings for a user in a guild
    returns an array of warning objects
    '''
    userID = str(userID)

    dataFile = path.join(path.dirname(__file__), 'Data/Users.json')
    # ToDo Claim lock
    with open(dataFile, 'r') as f:
        users = json.load(f)
    # check if the user exists, if not add them
    if (not user_exists(users, userID)):
        # if the user had to be created write back to the file
        with open(dataFile, 'w') as f:
            json.dump(users, f, indent=4)
    # ToDo Release lock

    result = []
    for warning in users[userID]['warnings']:
        if warning['guild'] == guildId:
            result.append(f"[id ({warning['id']}) at {warning['dateTime']}] "
                          f"{warning['warning']}")
    return(result)


def add_warning(user_id, guild_id, warning):
    user_id = str(user_id)
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    dataFile = path.join(path.dirname(__file__), 'Data/Users.json')

    # ToDo Claim Lock
    with open(dataFile, 'r') as f:
        users = json.load(f)
    # check if the user exists, if not add them
    user_exists(users, user_id)

    new_id = 0
    ids = []
    for warn in users[user_id]['warnings']:
        ids.append(warn['id'])
    if not ids:
        new_id = 1
    else:
        new_id = max(ids) + 1

    new_warning = {"id": new_id,
                   "dateTime": now,
                   "guild": guild_id,
                   "warning": warning}

    # {id: dateTime : guild : warning}
    users[user_id]['warnings'].append(new_warning)

    with open(dataFile, 'w') as f:
        json.dump(users, f, indent=4)
    # ToDo: Release Lock here
