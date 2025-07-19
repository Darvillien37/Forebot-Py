import random
from datetime import datetime, timezone
import sqlite3
from Database import Items
from Database import attributes
from Database.attributes import ATTR_UNSPENT_POINTS, ATTR_VITALITY, ATTR_BRAWN, ATTR_DEXTERITY, ATTR_MIND, ATTR_RESILIENCE, ATTR_AWARENESS
from Database.attributes import ATTR_WILLPOWER, ATTR_ACCURACY, ATTR_SPEED, ATTR_LUCK, ATTR_SMOOTH_TALKING
from Utils.utils import DAILY, WEEKLY, MONTHLY, TIME_FORMAT


_db_file = None


def roll_loot_tier():
    tiers = list(Items.LOOT_TIERS.keys())
    weights = [Items.LOOT_TIERS[t]['weight'] for t in tiers]
    return random.choices(tiers, weights=weights, k=1)[0]


def init_db(db_file):
    global _db_file
    _db_file = db_file
    __ensure_table_and_columns("users", {
                        "user_id": "INTEGER PRIMARY KEY",
                        "xp": "INTEGER DEFAULT 0",
                        "level": "INTEGER DEFAULT 1",
                        "coins": "INTEGER DEFAULT 0",
                        "last_daily": "TEXT DEFAULT NULL",
                        "last_weekly": "TEXT DEFAULT NULL",
                        "last_monthly": "TEXT DEFAULT NULL",
                        "last_voice_xp": "TEXT DEFAULT NULL"
                        })

    __ensure_table_and_columns("guilds", {
                        "guild_id": "INTEGER PRIMARY KEY",
                        "bot_spam_ch_id": "INTEGER DEFAULT NULL",
                        })

    __ensure_table_and_columns("items", {
                        "item_id": "INTEGER PRIMARY KEY",
                        "name": "TEXT DEFAULT NULL",
                        "description": "TEXT DEFAULT NULL",
                        "rarity": "TEXT DEFAULT NULL",
                        "price": "INTEGER DEFAULT 999999",
                        "type": f"TEXT DEFAULT {Items.TYPE_DEBUG}",
                        "emoji": "TEXT DEFAULT NULL"
                        })
    __ensure_table_and_columns("user_inventory", {
                        "user_id": "INTEGER",
                        "item_id": "INTEGER",
                        "quantity": "INTEGER DEFAULT 0",
                        },
                        {
                        "PRIMARY KEY (user_id, item_id)",
                        "FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE",
                        "FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE"
                        })
    Items.ensure_items_exist(_db_file)
    print("converting user boxes to items")
    user_lootboxes_to_items()
    __ensure_table_and_columns("user_attributes", {
                        "user_id": "INTEGER PRIMARY KEY",
                        ATTR_VITALITY: "INTEGER DEFAULT 0",
                        ATTR_BRAWN: "INTEGER DEFAULT 0",
                        ATTR_DEXTERITY: "INTEGER DEFAULT 0",
                        ATTR_MIND: "INTEGER DEFAULT 0",
                        ATTR_RESILIENCE: "INTEGER DEFAULT 0",
                        ATTR_AWARENESS: "INTEGER DEFAULT 0",
                        ATTR_WILLPOWER: "INTEGER DEFAULT 0",
                        ATTR_ACCURACY: "INTEGER DEFAULT 0",
                        ATTR_SPEED: "INTEGER DEFAULT 0",
                        ATTR_LUCK: "INTEGER DEFAULT 0",
                        ATTR_SMOOTH_TALKING: "INTEGER DEFAULT 0",
                        ATTR_UNSPENT_POINTS:  "INTEGER DEFAULT 10",
                        },
                        {
                        "FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE"
                        })
    __ensure_table_and_columns("attribute_modifiers", {
                        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                        "user_id": "INTEGER NOT NULL",
                        "source": "TEXT NOT NULL",  # e.g. "Potion of Might", "Event: Lunar Eclipse"
                        "expires_at": "TEXT NOT NULL",  # TIME_FORMAT
                        ATTR_VITALITY: "INTEGER DEFAULT 0",
                        ATTR_BRAWN: "INTEGER DEFAULT 0",
                        ATTR_DEXTERITY: "INTEGER DEFAULT 0",
                        ATTR_MIND: "INTEGER DEFAULT 0",
                        ATTR_RESILIENCE: "INTEGER DEFAULT 0",
                        ATTR_AWARENESS: "INTEGER DEFAULT 0",
                        ATTR_WILLPOWER: "INTEGER DEFAULT 0",
                        ATTR_ACCURACY: "INTEGER DEFAULT 0",
                        ATTR_SPEED: "INTEGER DEFAULT 0",
                        ATTR_LUCK: "INTEGER DEFAULT 0",
                        ATTR_SMOOTH_TALKING: "INTEGER DEFAULT 0",
                        },
                        {
                        "FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE"
                        })


def user_lootboxes_to_items():
    global _db_file
    columns = []
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in c.fetchall()]  # row[1] is the column name

    if "loot_common" not in columns:
        print("Database.user_lootboxes_to_items(): loot_common not in users table, can probably delete this function.")
        return

    ids = []
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        cmd = "SELECT user_id FROM users"
        c.execute(cmd)
        ids = c.fetchall()
    for id in ids:
        boxes = get_lootboxes_old(id[0])
        for tier in boxes:
            if boxes[tier] > 0:
                item_id = get_item_id_by_name(f"{tier.title()} Lootbox")
                update_inventory_item_quantity(id[0], item_id, boxes[tier])
                with sqlite3.connect(_db_file) as conn:
                    c = conn.cursor()
                    c.execute(f"UPDATE users SET loot_{tier} = 0 WHERE user_id = {id[0]}")
                    conn.commit()

    # delete the columns in the users table
    print("Deleting columns")
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        for tier in Items.LOOT_TIERS:
            c.execute(f"ALTER TABLE users DROP COLUMN loot_{tier}")
            conn.commit()


def __ensure_table_and_columns(table_name, columns: dict, extra_lines=None):
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
            extra = ""
            if extra_lines is not None:
                extra = ", " + (', '.join([f"{line}" for line in extra_lines]))
            create_stmt = f"CREATE TABLE {table_name} ({col_defs}{extra})"
            print(create_stmt)
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
        conn.commit()


def dt_testing():
    global _db_file
    check_user(202112441457442816)
    commands = [
            "UPDATE users SET xp=1000, level=1 WHERE user_id=202112441457442816",
    ]
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        for cmd in commands:
            c.execute(cmd)
            conn.commit()


# ------------------ USER STUFF ------------------
def check_user(user_id):
    global _db_file
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        c.execute("INSERT OR IGNORE INTO user_attributes (user_id) VALUES (?)", (user_id,))
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
        c.execute(f'UPDATE users SET coins = coins + {delta} WHERE user_id = {user_id}')
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


# ------------------ INVENTORY STUFF ------------------
def update_inventory_item_quantity(user_id: int, item_id: int, delta: int):
    global _db_file
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        cmd = f"SELECT quantity FROM user_inventory WHERE user_id={user_id} AND item_id={item_id}"
        c.execute(cmd)
        item_qty = c.fetchone()
        if item_qty is None:
            # not already in users inventory, add it.
            if delta > 0:
                cmd = "INSERT INTO user_inventory (user_id, item_id, quantity) VALUES"
                cmd += f" ({user_id}, {item_id}, {delta})"
                c.execute(cmd)
        else:
            quantity_str = ""
            if (item_qty[0] + delta) > 0:
                quantity_str = f"quantity+{delta}"
            else:
                quantity_str = "0"
            cmd = f"UPDATE user_inventory SET quantity={quantity_str}"
            cmd += f" WHERE user_id={user_id} AND item_id={item_id}"
            c.execute(cmd)
        conn.commit()


def get_item_id_by_name(item_name: str):
    global _db_file
    id = []
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute(f"SELECT item_id FROM items WHERE LOWER(name) LIKE LOWER(\"{item_name}\")")
        id = c.fetchone()
    if id is None:
        return None
    return id[0]


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
    item_id = Items.LOOT_TIERS[tier]["box_id"]
    if item_id is not None:
        update_inventory_item_quantity(user_id, item_id, 1)


def add_lootbox_old(user_id, tier):
    check_user(user_id)
    col = f"loot_{tier}"
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute(f'UPDATE users SET {col} = {col} + 1 WHERE user_id = ?', (user_id,))
        conn.commit()


def get_lootboxes(user_id):
    global _db_file
    db_rows = []
    # Get all lootboxes from the user's inventory
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        ids = []
        for box_tier in Items.LOOT_TIERS:
            ids.append(str(Items.LOOT_TIERS[box_tier]["box_id"]))
        ids_str = ", ".join(ids)
        cmd = f"SELECT user_id, item_id, quantity FROM user_inventory WHERE user_id={user_id} AND item_id IN ({ids_str})"
        c.execute(cmd)
        db_rows = c.fetchall()

    # Create the dictionary to return
    # Build a reverse lookup: item_id -> tier name
    box_id_to_tier = {v["box_id"]: k for k, v in Items.LOOT_TIERS.items()}
    # Initialise result with all tiers as 0
    result = {tier: 0 for tier in Items.LOOT_TIERS}
    # Update the ones with rows in the database
    for row in db_rows:
        item_id = row[1]
        quantity = row[2]
        if item_id in box_id_to_tier:
            tier = box_id_to_tier[item_id]
            result[tier] = quantity

    return result


def get_lootboxes_old(user_id):
    check_user(user_id)
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        tier_columns = [f"loot_{tier}" for tier in Items.LOOT_TIERS]
        c.execute(f'''
            SELECT {", ".join(tier_columns)} FROM users WHERE user_id = ?
        ''', (user_id,))
        row = c.fetchone()
        return dict(zip(Items.LOOT_TIERS.keys(), row))


def claim_specific_lootbox(user_id: int, tier: str):
    row = []
    item_id = Items.LOOT_TIERS[tier]["box_id"]
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute(f'SELECT quantity FROM user_inventory WHERE user_id = {user_id} AND item_id = {item_id}')
        row = c.fetchone()
    if not row or row[0] < 1:
        return None
    reward = random.randint(Items.LOOT_TIERS[tier]["min"], Items.LOOT_TIERS[tier]["max"])
    update_inventory_item_quantity(user_id, item_id, -1)
    update_coins(user_id, reward)
    return reward


def claim_specific_lootbox_old(user_id, tier):
    check_user(user_id)
    tier_column = f"loot_{tier}"
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute(f'SELECT {tier_column}, coins FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        if not row or row[0] < 1:
            return None

        reward = random.randint(Items.LOOT_TIERS[tier]["min"], Items.LOOT_TIERS[tier]["max"])
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


# ------------------ Attributes STUFF ------------------

def get_user_attributes(user_id: int):
    check_user(user_id)
    attr_columns = ', '.join(attr for attr in attributes.ATTR_LIST)
    with sqlite3.connect(_db_file) as conn:
        c = conn.cursor()
        c.execute(f"SELECT {attr_columns}, {ATTR_UNSPENT_POINTS} FROM user_attributes WHERE user_id = {user_id}")
        row = c.fetchone()
        if not row:
            c.execute(f"INSERT INTO user_attributes (user_id) VALUES ({user_id})")
            conn.commit()
            row = ((0,) * len(attributes.ATTR_LIST)) + (10,)   # All stats and 10 unspent
        keys = [col[0] for col in c.description]
        keys.append(ATTR_UNSPENT_POINTS)
        return dict(zip(keys, row))


def increase_attribute(user_id: int, attribute: str):
    if attribute in attributes.ATTR_LIST:
        with sqlite3.connect(_db_file) as conn:
            c = conn.cursor()
            c.execute(f"""
                UPDATE user_attributes
                SET {attribute} = {attribute} + 1, {ATTR_UNSPENT_POINTS} = {ATTR_UNSPENT_POINTS} - 1
                WHERE user_id = {user_id} AND unspent_points > 0
            """)
            conn.commit()
