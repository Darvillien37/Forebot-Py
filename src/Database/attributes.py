import discord

ATTR_BASE_POINTS = 10

ATTR_VITALITY = "vitality"
ATTR_BRAWN = "brawn"
ATTR_DEXTERITY = "dexterity"
ATTR_MIND = "mind"
ATTR_RESILIENCE = "resilience"
ATTR_AWARENESS = "awareness"
ATTR_WILLPOWER = "willpower"
ATTR_ACCURACY = "accuracy"
ATTR_SPEED = "speed"
ATTR_LUCK = "luck"
ATTR_SMOOTH_TALKING = "smooth_talking"

ATTR_UNSPENT_POINTS = "unspent_points"

ATTR_LIST = {
    ATTR_VITALITY:       {"emoji": "❤️",    "description": "Increases max HP and ???."},
    ATTR_BRAWN:          {"emoji": "💪",    "description": "Boosts melee damage and coin gain from loot."},
    ATTR_DEXTERITY:      {"emoji": "🤸",    "description": "Improves ranged damage and ???."},
    ATTR_MIND:           {"emoji": "🧠",    "description": "Amplifies magic damage and passive XP gain."},
    ATTR_RESILIENCE:     {"emoji": "🛡️",    "description": "Reduces melee damage taken, Resistance to debuffs, and reduces penalties."},
    ATTR_AWARENESS:      {"emoji": "👁️",    "description": "Reduces ranged damage, improves detection, and ???."},
    ATTR_WILLPOWER:      {"emoji": "🧘",    "description": "Reduces incoming Magic damage, chance to not faint on fatal damage, "
                          "and bonuses when maintaining claim streaks."},
    ATTR_ACCURACY:       {"emoji": "🎯",    "description": "Increases chance to land attacks and ???."},
    ATTR_SPEED:          {"emoji": "🏃",    "description": "Determines turn order, and reduction on claim cool-downs."},
    ATTR_LUCK:           {"emoji": "🍀",    "description": "Increases critical hit chance and loot quality chances."},
    ATTR_SMOOTH_TALKING: {"emoji": "🗣️",    "description": "Chance to distract or confuse enemies, and better deals with NPCs."},
}


def build_attribute_embed(user: discord.Member, data, show_descriptions: bool):
    embed = discord.Embed(title=f"{user.display_name}'s Attributes", color=discord.Color.blurple())
    for key in data:
        if key in ATTR_LIST:
            desc = f"\n- {ATTR_LIST[key]['description']}" if show_descriptions else ""
            embed.add_field(name=f"{ATTR_LIST[key]['emoji']} {key.title()}", value=f"{str(data[key])}{desc}", inline=True)
    embed.set_footer(text=f"Unspent Points: {data['unspent_points']}")
    embed.set_thumbnail(url=user.display_avatar.url)
    return embed


def get_bonus_points_upto_level(level: int) -> int:
    total = ATTR_BASE_POINTS
    for i in range(0, level + 1):
        total += get_bonus_points_for_this_level(i)
    return total


def get_bonus_points_for_this_level(level: int) -> int:
    if level == 0:
        return 0
    points: int = 1  # default 1 point
    if level % 5 == 0:
        points += 1
    if level % 10 == 0:
        points += 1
    if level % 50 == 0:
        points += 2
    if level % 100 == 0:
        points += 2
    return points
