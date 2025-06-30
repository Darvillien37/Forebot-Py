from random import randint


def get_xp_from_message(message: str):
    '''
    Get an amount of XP based off a message string
    '''
    # the smallest maximum amount
    minMax = int(len(message) / 3)
    if minMax < 3:
        minMax = 3
    amount = randint(1, minMax)
    return amount


def get_xp_threshold(currLvl):
    return int((3 * pow(currLvl, 1.5)) + 50)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    # Generate x values (non-negative because of x^1.5)
    x = np.linspace(0, 100, 400)
    y = get_xp_threshold(x)

    # Plot
    plt.figure(figsize=(8, 5))
    plt.plot(x, y, label=r'$y = 3x^{1.5} + 100$', color='blue')
    plt.xlabel('Level')
    plt.ylabel('XP')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
