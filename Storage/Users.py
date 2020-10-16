from os import path
import json
from . import XP
from datetime import datetime


def user_exists(users, user_id: str, guild_id=None):
    '''
    Checks if the user exists, and if not creates it.
    Returns true if the user already existed, false if they had to be created or modified
    '''
    # assume users did not have to be modified
    modified: bool = False

    if user_id not in users:
        users[user_id] = {}
        users[user_id]['experience'] = 0
        users[user_id]['level'] = 0
        users[user_id]['inGuilds'] = []
        users[user_id]['warnings'] = []
        modified = True

    if 'inGuilds' not in users[user_id]:
        users[user_id]['inGuilds'] = []
        modified = True
    if (guild_id is not None) and (guild_id not in users[user_id]['inGuilds']):
        users[user_id]['inGuilds'].append(guild_id)
        modified = True

    if 'warnings' not in users[user_id]:
        users[user_id]['warnings'] = []
        modified = True

    # flip due to the nature of how this method returns
    return not modified


def GiveXP(userID: str, xpAmount, guild_id):
    '''
    Give XP to a user.
    Keyword arguments:
    userID -- the users id to give xp to.
    xpAmount -- the amount of xp to give to the user.
    guild_id -- force the user in the guild they wrote in (shouldn't be in here but meh)
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
    user_exists(users, userID, guild_id)

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
    if (not user_exists(users, userID, guildId)):
        # if the user had to be created write back to the file
        with open(dataFile, 'w') as f:
            json.dump(users, f, indent=4)
    # ToDo Release lock

    result = []
    for warning in users[userID]['warnings']:
        if warning['guild'] == guildId:
            result.append(warning)
    return(result)


def add_warning(user_id, guild_id, warning):
    user_id = str(user_id)
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    dataFile = path.join(path.dirname(__file__), 'Data/Users.json')

    # ToDo Claim Lock
    with open(dataFile, 'r') as f:
        users = json.load(f)
    # check if the user exists, if not add them
    user_exists(users, user_id, guild_id)

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


def remove_warning(user_id, warning_id):
    user_id = str(user_id)
    dataFile = path.join(path.dirname(__file__), 'Data/Users.json')

    # ToDo Claim Lock
    with open(dataFile, 'r') as f:
        users = json.load(f)
    # check if the user exists, if not add them
    user_exists(users, user_id)
    # get warnings list
    warnings = users[user_id]['warnings']

    # check if id exists in warnings list
    id_found = False
    for warning in warnings:
        if warning['id'] == warning_id:
            id_found = True
            break

    # if not exists, return false
    if not id_found:
        return False

    users[user_id]['warnings'].remove(warning)

    with open(dataFile, 'w') as f:
        json.dump(users, f, indent=4)
    # ToDo: Release Lock here
    return True


def edit_warning_text(user_id, warning_id, new_warning):
    user_id = str(user_id)
    dataFile = path.join(path.dirname(__file__), 'Data/Users.json')

    # ToDo Claim Lock
    with open(dataFile, 'r') as f:
        users = json.load(f)
    # check if the user exists, if not add them
    user_exists(users, user_id)
    # get warnings list
    warnings = users[user_id]['warnings']

    # check if id exists in warnings list
    id_found = False
    for warning in warnings:
        if warning['id'] == warning_id:
            warning['warning'] = new_warning
            id_found = True
            break

    # if not exists, return false
    if not id_found:
        return False

    with open(dataFile, 'w') as f:
        json.dump(users, f, indent=4)
    # ToDo: Release Lock here
    return True


def clear_expired_warnings():
    dataFile = path.join(path.dirname(__file__), 'Data/Users.json')
    with open(dataFile, 'r') as f:
        users = json.load(f)

    for user in users:
        for warning in users[user]['warnings']:
            warningDT = datetime.strptime(warning['dateTime'], "%d/%m/%Y %H:%M:%S")

            warning_age = datetime.now() - warningDT
            # if the warning is older than 30 days
            if(warning_age.days > 30):
                remove_warning(user, warning['id'])


def get_info(user_id, guild_id):
    user_id = str(user_id)

    dataFile = path.join(path.dirname(__file__), 'Data/Users.json')
    # ToDo Claim lock
    with open(dataFile, 'r') as f:
        users = json.load(f)
    # check if the user exists, if not add them
    if (not user_exists(users, user_id, guild_id)):
        # if the user had to be created write back to the file
        with open(dataFile, 'w') as f:
            json.dump(users, f, indent=4)
    # ToDo Release lock
    xp_for_next_level = int(XP.calculate_xp_for_next_level(users[user_id]['level']))
    info = []
    info.append(f"Level:{users[user_id]['level']}")
    info.append(f"Experience:{users[user_id]['experience']} / {xp_for_next_level}")
    warnCount = 0
    for warning in users[user_id]['warnings']:
        if warning['guild'] == guild_id:
            warnCount = warnCount + 1

    info.append(f"Guild Warnings:{warnCount}")

    return info


def force_update_users():
    # force update the users data to have all the keys
    dataFile = path.join(path.dirname(__file__), 'Data/Users.json')
    # ToDo Claim lock
    with open(dataFile, 'r') as f:
        users = json.load(f)

    for user_id in users:
        user_exists(users, user_id)
        # check if the user exists, if not add them

    with open(dataFile, 'w') as f:
        json.dump(users, f, indent=4)
    # ToDo Release lock


def add_guild(user_id, guild_id):
    user_id = str(user_id)
    dataFile = path.join(path.dirname(__file__), 'Data/Users.json')

    # ToDo Claim Lock
    with open(dataFile, 'r') as f:
        users = json.load(f)
    # check if the user exists, if not add them
    user_exists(users, user_id)

    if guild_id not in users[user_id]['inGuilds']:
        users[user_id]['inGuilds'].append(guild_id)

    with open(dataFile, 'w') as f:
        json.dump(users, f, indent=4)
    # ToDo: Release Lock here


def remove_guild(user_id, guild_id):
    user_id = str(user_id)
    dataFile = path.join(path.dirname(__file__), 'Data/Users.json')

    # ToDo Claim Lock
    with open(dataFile, 'r') as f:
        users = json.load(f)

    modified = False
    if user_id in users:
        if guild_id in users[user_id]['inGuilds']:
            users[user_id]['inGuilds'].remove(guild_id)
            modified = True

    if modified:
        with open(dataFile, 'w') as f:
            json.dump(users, f, indent=4)
    # ToDo: Release Lock here


def top_ten(guild_id):
    dataFile = path.join(path.dirname(__file__), 'Data/Users.json')
    # ToDo Claim lock
    with open(dataFile, 'r') as f:
        users = json.load(f)
    # ToDo Release lock

    users_in_guild = []
    for user_id in users:
        if guild_id in users[user_id]['inGuilds']:
            users_in_guild.append({
                    "ID": user_id,
                    "level": users[user_id]['level'],
                    "experience": users[user_id]['experience']
                })

    # sort and get the top 10
    sorted_top_ten = sorted(users_in_guild, key=lambda k: (int(k['level']), int(k["experience"])), reverse=True)[:10]
    for tt in sorted_top_ten:
        tt['experience'] = f"{tt['experience']} / {int(XP.calculate_xp_for_next_level(tt['level']))}"
    return sorted_top_ten
