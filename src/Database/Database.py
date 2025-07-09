import random
from datetime import datetime, timezone
import sqlite3
from Utils.utils import DAILY, WEEKLY, MONTHLY, TIME_FORMAT


_db_file = None
LOOT_TIERS = {
    "common":    {"weight": 50, "min": 5,  "max": 10,   "emoji": "🟤", "color": 0x964B00},  # Brown
    "uncommon":  {"weight": 25, "min": 10, "max": 50,   "emoji": "🟢", "color": 0x2ecc71},  # Green
    "rare":      {"weight": 12, "min": 50, "max": 200,   "emoji": "🔵", "color": 0x3498db},  # Blue
    "epic":      {"weight": 7,  "min": 200, "max": 500,   "emoji": "🟣", "color": 0x9b59b6},  # Purple
    "legendary": {"weight": 4,  "min": 500, "max": 1000,  "emoji": "🟠", "color": 0xe67e22},  # Orange
    "mythic":    {"weight": 2,  "min": 1000, "max": 2000, "emoji": "🟡", "color": 0xd4af37},  # Gold
}


def roll_loot_tier():
    tiers = list(LOOT_TIERS.keys())
    weights = [LOOT_TIERS[t]['weight'] for t in tiers]
    return random.choices(tiers, weights=weights, k=1)[0]


def init_db(db_file):
    global _db_file
    _db_file = db_file
    __ensure_table_and_columns("users", {
                        "user_id": "INTEGER PRIMARY KEY",
                        "xp": "INTEGER DEFAULT 0",
                        "level": "INTEGER DEFAULT 1",
                        "coins": "INTEGER DEFAULT 0",
                        "loot_common": "INTEGER DEFAULT 0",
                        "loot_uncommon": "INTEGER DEFAULT 0",
                        "loot_rare": "INTEGER DEFAULT 0",
                        "loot_epic": "INTEGER DEFAULT 0",
                        "loot_legendary": "INTEGER DEFAULT 0",
                        "loot_mythic": "INTEGER DEFAULT 0",
                        "last_daily": "TEXT DEFAULT NULL",
                        "last_weekly": "TEXT DEFAULT NULL",
                        "last_monthly": "TEXT DEFAULT NULL",
                        "last_voice_xp": "TEXT DEFAULT NULL"
                        })

    __ensure_table_and_columns("guilds", {
                        "guild_id": "INTEGER PRIMARY KEY",
                        "bot_spam_ch_id": "INTEGER DEFAULT NULL",
                        })


def __ensure_table_and_columns(table_name, columns: dict):
    """
    Ensure the table exists, and has all the specified columns.
    :param table_name: Name of the table to check
    :param columns: Dict of column_name: column_definition
                    e.g., {"coins": "INTEGER DEFAULT 0", "xp": "INTEGER DEFAULT 0"}
    """
    with sqlite3.connect(_db_file) as conn:
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        exists = cursor.fetchone()

        if not exists:
            # Create table from scratch
            col_defs = ', '.join([f"{name} {definition}" for name, definition in columns.items()])
            create_stmt = f"CREATE TABLE {table_name} ({col_defs})"
            cursor.execute(create_stmt)
            print(f"Created table {table_name}")
        else:
            # Get existing columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_cols = {row[1] for row in cursor.fetchall()}

            # Add missing columns
            for col, definition in columns.items():
                if col not in existing_cols:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {definition}")
                    print(f"Added missing column '{col}' to {table_name}")


def dt_testing():
    global _db_file
    check_user(202112441457442816)
    commands = [
            # "UPDATE users SET xp=1000, level=1 WHERE user_id=202112441457442816",
    ]
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        for cmd in commands:
            c.execute(cmd)
            conn.commit()
    # add_lootbox(202112441457442816, roll_loot_tier())
    print(f"voice: {get_last_voice_xp(202112441457442816)}")


def get_coins(user_id):
    check_user(user_id)
    global _db_file
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute('SELECT coins FROM users WHERE user_id=?', (user_id,))
        coins = c.fetchone()
        if not coins:
            return 0
        return coins[0]


def update_coins(user_id: int, delta: int):
    check_user(user_id)
    global _db_file
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute('UPDATE users SET coins = coins + ? WHERE user_id = ?', (delta, user_id))
        conn.commit()


# ------------------ USER STUFF ------------------

def check_user(user_id):
    global _db_file
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
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


def get_user_xp_level(user_id):
    global _db_file
    check_user(user_id)
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute('SELECT xp, level FROM users WHERE user_id=?', (user_id,))
        data = c.fetchone()
        if not data:
            return (0, 1)
        return (data[0], data[1])


def set_user_xp_level(user_id, xp, level):
    global _db_file
    check_user(user_id)
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute('''UPDATE users SET xp=?, level=?
                     WHERE user_id=?''', (xp, level, user_id))
        conn.commit()


def update_user(user_id, xp, level, coins):
    global _db_file
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute('''UPDATE users SET xp=?, level=?, coins=?
                     WHERE user_id=?''', (xp, level, coins, user_id))
        conn.commit()


def get_all_user_ids(file=None):
    if file is None:
        path = _db_file
    else:
        path = file

    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.execute('SELECT user_id FROM users')
        user_ids = c.fetchall()
        return user_ids


# ------------------ VOICE STUFF ------------------

def get_last_voice_xp(user_id):
    check_user(user_id)
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute(f"SELECT last_voice_xp FROM users WHERE user_id = {user_id}")
        row = c.fetchone()
        if not row or row[0] is None:
            return None
        return datetime.strptime(row[0], TIME_FORMAT).replace(tzinfo=timezone.utc)


def update_last_voice_xp(user_id):
    check_user(user_id)
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        now = datetime.now(timezone.utc).strftime(TIME_FORMAT)
        c.execute("UPDATE users SET last_voice_xp = ? WHERE user_id = ?", (now, user_id))
        conn.commit()


def clear_last_voice_xp(user_id):
    check_user(user_id)
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET last_voice_xp = NULL WHERE user_id = ?", (user_id,))
        conn.commit()


# ------------------ LOOTBOX STUFF ------------------

def add_lootbox(user_id, tier):
    check_user(user_id)
    col = f"loot_{tier}"
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute(f'UPDATE users SET {col} = {col} + 1 WHERE user_id = ?', (user_id,))
        conn.commit()


def get_lootboxes(user_id):
    check_user(user_id)
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        tier_columns = [f"loot_{tier}" for tier in LOOT_TIERS]
        c.execute(f'''
            SELECT {", ".join(tier_columns)} FROM users WHERE user_id = ?
        ''', (user_id,))
        row = c.fetchone()
        return dict(zip(LOOT_TIERS.keys(), row))


def get_highest_tier_lootbox(user_id):
    check_user(user_id)
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        tier_columns = [f"loot_{t}" for t in LOOT_TIERS]
        # Get the all loot box tiers the user has
        c.execute(f'SELECT {", ".join(tier_columns)} FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        tier_counts = dict(zip(LOOT_TIERS.keys(), row))
        # Check from highest to lowest tier
        for tier in reversed(list(LOOT_TIERS.keys())):
            # return that tier if the user has that type
            if tier_counts[tier] > 0:
                return tier
    # otherwise the user has no loot boxes, return none
    return None


def claim_specific_lootbox(user_id, tier):
    check_user(user_id)
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


def get_claim_timestamps(user_id):
    check_user(user_id)
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute('SELECT last_daily, last_weekly, last_monthly FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        if not row:
            return None
        return dict(zip([DAILY, WEEKLY, MONTHLY], row))


def update_claim_timestamp(user_id, claim_type):
    check_user(user_id)
    now_str = datetime.now(timezone.utc).strftime(TIME_FORMAT)
    col = f'last_{claim_type}'
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute(f'UPDATE users SET {col} = ? WHERE user_id = ?', (now_str, user_id))
        conn.commit()


# ------------------ Guild STUFF ------------------

def check_guild(guild_id: int):
    global _db_file
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO guilds (guild_id) VALUES (?)", (guild_id,))
        conn.commit()


def get_guild_spam_channel_id(guild_id: int):
    check_guild(guild_id)
    global _db_file
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute('SELECT bot_spam_ch_id FROM guilds WHERE guild_id=?', (guild_id,))
        ch_id = c.fetchone()
        if not ch_id:
            return None
        return ch_id[0]


def set_guild_spam_channel_id(guild_id: int, channel_id: int):
    check_guild(guild_id)
    global _db_file
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute('UPDATE guilds SET bot_spam_ch_id = ? WHERE guild_id = ?', (channel_id, guild_id))
        conn.commit()
