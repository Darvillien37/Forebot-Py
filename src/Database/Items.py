import sqlite3


TYPE_DEBUG = "debug"
TYPE_COSMETIC = "cosmetic"
TYPE_CONSUMABLE = "consumable"
TYPE_LOOTBOX = "lootbox"

TIER_COMMON = "common"
TIER_UNCOMMON = "uncommon"
TIER_RARE = "rare"
TIER_EPIC = "epic"
TIER_LEGENDARY = "legendary"
TIER_MYTHIC = "mythic"

COMMON_LOOTBOX_ID = 1
UNCOMMON_LOOTBOX_ID = 2
RARE_LOOTBOX_ID = 3
EPIC_LOOTBOX_ID = 4
LEGENDARY_LOOTBOX_ID = 5
MYTHIC_LOOTBOX_ID = 6

LOOT_TIERS = {
 TIER_COMMON:    {"weight": 500, "min": 5, "max": 10, "box_id": COMMON_LOOTBOX_ID, "emoji": "🟤", "color": 0x964B00},  # Brown
 TIER_UNCOMMON:  {"weight": 400, "min": 10, "max": 50, "box_id": UNCOMMON_LOOTBOX_ID, "emoji": "🟢", "color": 0x2ecc71},  # Green
 TIER_RARE:      {"weight": 200, "min": 50, "max": 200, "box_id": RARE_LOOTBOX_ID, "emoji": "🔵", "color": 0x3498db},  # Blue
 TIER_EPIC:      {"weight": 100, "min": 200, "max": 500, "box_id": EPIC_LOOTBOX_ID, "emoji": "🟣", "color": 0x9b59b6},  # Purple
 TIER_LEGENDARY: {"weight": 50, "min": 500, "max": 1000, "box_id": LEGENDARY_LOOTBOX_ID, "emoji": "🟠", "color": 0xe67e22},  # Orange
 TIER_MYTHIC:    {"weight": 1, "min": 1000, "max": 2000, "box_id": MYTHIC_LOOTBOX_ID, "emoji": "✨", "color": 0xd4af37},  # Gold
}

ITEM_TYPES = [TYPE_DEBUG,
              TYPE_COSMETIC,
              TYPE_CONSUMABLE,
              TYPE_LOOTBOX
              ]

ALL_ITEMS = {
    COMMON_LOOTBOX_ID: {
        "name": "Common Lootbox",
        "description": "A basic wooden box with a small handful of simple rewards.",
        "rarity": TIER_COMMON,
        "price": int(LOOT_TIERS[TIER_COMMON]["min"] +
                     ((LOOT_TIERS[TIER_COMMON]["max"] - LOOT_TIERS[TIER_COMMON]["min"])*0.75)),
        "type": TYPE_LOOTBOX,
        "emoji": LOOT_TIERS[TIER_COMMON]["emoji"]
       },
    UNCOMMON_LOOTBOX_ID: {
        "name": "Uncommon Lootbox",
        "description": "A lightly enchanted crate containing modest but useful treasures.",
        "rarity": TIER_UNCOMMON,
        "price": int(LOOT_TIERS[TIER_UNCOMMON]["min"] +
                     ((LOOT_TIERS[TIER_UNCOMMON]["max"] - LOOT_TIERS[TIER_UNCOMMON]["min"])*0.75)),
        "type": TYPE_LOOTBOX,
        "emoji": LOOT_TIERS[TIER_UNCOMMON]["emoji"]
       },
    RARE_LOOTBOX_ID: {
        "name": "Rare Lootbox",
        "description": "A finely crafted chest with valuable and rarer rewards inside.",
        "rarity": TIER_RARE,
        "price": int(LOOT_TIERS[TIER_RARE]["min"] +
                     ((LOOT_TIERS[TIER_RARE]["max"] - LOOT_TIERS[TIER_RARE]["min"])*0.75)),
        "type": TYPE_LOOTBOX,
        "emoji": LOOT_TIERS[TIER_RARE]["emoji"]
       },
    EPIC_LOOTBOX_ID: {
        "name": "Epic Lootbox",
        "description": "A magical box filled with powerful loot fit for seasoned adventurers.",
        "rarity": TIER_EPIC,
        "price": int(LOOT_TIERS[TIER_EPIC]["min"] +
                     ((LOOT_TIERS[TIER_EPIC]["max"] - LOOT_TIERS[TIER_EPIC]["min"])*0.75)),
        "type": TYPE_LOOTBOX,
        "emoji": LOOT_TIERS[TIER_EPIC]["emoji"]
       },
    LEGENDARY_LOOTBOX_ID: {
        "name": "Legendary Lootbox",
        "description": "A radiant chest of rare wonders and highly coveted riches.",
        "rarity": TIER_LEGENDARY,
        "price": int(LOOT_TIERS[TIER_LEGENDARY]["min"] +
                     ((LOOT_TIERS[TIER_LEGENDARY]["max"] - LOOT_TIERS[TIER_LEGENDARY]["min"])*0.75)),
        "type": TYPE_LOOTBOX,
        "emoji": LOOT_TIERS[TIER_LEGENDARY]["emoji"]
       },
    MYTHIC_LOOTBOX_ID: {
        "name": "Mythic Lootbox",
        "description": "A mysterious, otherworldly box containing treasures of immense value.",
        "rarity": TIER_MYTHIC,
        "price": int(LOOT_TIERS[TIER_MYTHIC]["min"] +
                     ((LOOT_TIERS[TIER_MYTHIC]["max"] - LOOT_TIERS[TIER_MYTHIC]["min"])*0.75)),
        "type": TYPE_LOOTBOX,
        "emoji": LOOT_TIERS[TIER_MYTHIC]["emoji"]
       },

}


def ensure_items_exist(db_file):
    with sqlite3.connect(db_file) as conn:
        c = conn.cursor()
        for item_id in ALL_ITEMS:
            # Find the Item in the database
            c.execute(f"SELECT * FROM items WHERE item_id={item_id}")
            result = c.fetchone()
            if result is None:
                # If the item doesn't exist, add it to the database
                print(f"{item_id} does not exist, adding to items table.")
                columns = ', '.join([f"{coll}" for coll in ALL_ITEMS[item_id]])
                values = ', '.join([f"\"{value}\"" for value in ALL_ITEMS[item_id].values()])
                cmd = f"INSERT INTO items (item_id, {columns}) VALUES ({item_id}, {values})"
                print(cmd)
                c.execute(cmd)
            else:
                # If the item does exist, check all the values in the column are correct
                for value in ALL_ITEMS[item_id].values():
                    if value not in result:
                        # if not then update the item.
                        print(f"Item Problem: ({value}) not in {result}")
                        col_defs = ', '.join([f"{col} = \"{value}\"" for col, value in ALL_ITEMS[item_id].items()])
                        cmd = f"UPDATE items SET {col_defs} WHERE item_id = {item_id};"
                        print(f"Updating: {cmd}")
                        c.execute(cmd)
                        # item updated, move on to the next
                        break


if __name__ == "__main__":
    total = 0
    for tier in LOOT_TIERS:
        total += LOOT_TIERS[tier]["weight"]
    print(f"Total: {total}")
    for tier in LOOT_TIERS:
        percent = round((LOOT_TIERS[tier]["weight"] / total) * 100, 3)
        print(f"{tier.title()}: {percent}%")
