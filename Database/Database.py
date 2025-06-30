import random
import sqlite3

_db_file = None
LOOT_TIERS = {
    "common":    {"weight": 50, "min": 50,  "max": 100,   "emoji": "🟤", "color": 0x964B00},  # Brown
    "uncommon":  {"weight": 25, "min": 100, "max": 200,   "emoji": "🟢", "color": 0x2ecc71},  # Green
    "rare":      {"weight": 12, "min": 200, "max": 400,   "emoji": "🔵", "color": 0x3498db},  # Blue
    "epic":      {"weight": 7,  "min": 400, "max": 800,   "emoji": "🟣", "color": 0x9b59b6},  # Purple
    "legendary": {"weight": 4,  "min": 800, "max": 1600,  "emoji": "🟠", "color": 0xe67e22},  # Orange
    "mythic":    {"weight": 2,  "min": 1600, "max": 3000, "emoji": "🟡", "color": 0xd4af37},  # Gold
}


def roll_loot_tier():
    tiers = list(LOOT_TIERS.keys())
    weights = [LOOT_TIERS[t]['weight'] for t in tiers]
    return random.choices(tiers, weights=weights, k=1)[0]


def init_db(db_file):
    global _db_file
    _db_file = db_file
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER,
                        xp INTEGER DEFAULT 0,
                        level INTEGER DEFAULT 1,
                        coins INTEGER DEFAULT 0,
                        loot_common INTEGER DEFAULT 0,
                        loot_uncommon INTEGER DEFAULT 0,
                        loot_rare INTEGER DEFAULT 0,
                        loot_epic INTEGER DEFAULT 0,
                        loot_legendary INTEGER DEFAULT 0,
                        loot_mythic INTEGER DEFAULT 0,
                        PRIMARY KEY (user_id)
                    )''')
        conn.commit()


def update_db():
    global _db_file
    commands = [
            "UPDATE users SET xp=101, level=1 WHERE user_id=202112441457442816",
            # "ALTER TABLE users ADD COLUMN loot_common INTEGER DEFAULT 0;",
            # "ALTER TABLE users ADD COLUMN loot_uncommon INTEGER DEFAULT 0;",
            # "ALTER TABLE users ADD COLUMN loot_rare INTEGER DEFAULT 0;",
            # "ALTER TABLE users ADD COLUMN loot_epic INTEGER DEFAULT 0;",
            # "ALTER TABLE users ADD COLUMN loot_legendary INTEGER DEFAULT 0;",
            # "ALTER TABLE users ADD COLUMN loot_mythic INTEGER DEFAULT 0;",
    ]
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        for cmd in commands:
            c.execute(cmd)
            conn.commit()


def get_user(user_id):
    global _db_file
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute('SELECT user_id, xp, level, coins FROM users WHERE user_id=?', (user_id,))
        user = c.fetchone()
        if not user:
            c.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
            conn.commit()
            return (user_id, 0, 1, 0)
        return user


def add_coins(user_id, delta):
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute('UPDATE users SET coins = coins + ? WHERE user_id = ?', (delta, user_id))
        conn.commit()


def update_user(user_id, xp, level, coins):
    global _db_file
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute('''UPDATE users SET xp=?, level=?, coins=?
                     WHERE user_id=?''', (xp, level, coins, user_id))
        conn.commit()


def add_lootbox(user_id, tier):
    col = f"loot_{tier}"
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute(f'UPDATE users SET {col} = {col} + 1 WHERE user_id = ?', (user_id,))
        conn.commit()


def get_lootboxes(user_id):
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        tier_columns = [f"loot_{tier}" for tier in LOOT_TIERS]
        c.execute(f'''
            SELECT {", ".join(tier_columns)} FROM users WHERE user_id = ?
        ''', (user_id,))
        row = c.fetchone()
        return row


def claim_lootbox(user_id):
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        tier_columns = [f"loot_{t}" for t in LOOT_TIERS]
        c.execute(f'SELECT {", ".join(tier_columns)}, coins FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        coin_total = row[-1]
        tier_counts = dict(zip(LOOT_TIERS.keys(), row[:-1]))

        # Check from highest to lowest tier
        for tier in reversed(list(LOOT_TIERS.keys())):
            if tier_counts[tier] > 0:
                reward = random.randint(LOOT_TIERS[tier]["min"], LOOT_TIERS[tier]["max"])
                coin_total += reward
                tier_column = f"loot_{tier}"
                c.execute(f'''
                    UPDATE users SET {tier_column} = {tier_column} - 1, coins = ? WHERE user_id = ?
                ''', (coin_total, user_id))
                conn.commit()
                return tier, reward

        return None  # No lootboxes


def claim_specific_lootbox(user_id, tier):
    tier_column = f"loot_{tier}"
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute(f'SELECT {tier_column}, coins FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        if not row or row[0] < 1:
            return None

        reward = random.randint(LOOT_TIERS[tier]["min"], LOOT_TIERS[tier]["max"])
        coin_total = row[1] + reward
        c.execute(f'''
            UPDATE users SET {tier_column} = {tier_column} - 1, coins = ? WHERE user_id = ?
        ''', (coin_total, user_id))
        conn.commit()
        return reward
