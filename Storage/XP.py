from random import randint


def getXPFromMessage(message: str):
    '''
    Get an amount of XP based off a message string
    '''
    # the smallest maximum amount
    minMax = int(len(message) / 3)
    if minMax < 3:
        minMax = 3
    amount = randint(1, minMax)
    return amount


def calculate_xp_for_next_level(currLvl):
    return (3 * pow(currLvl, 1.5)) + 100
