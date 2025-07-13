from discord.ext import commands
import discord
from Database import Database, Items


# Doesn't need to be in class, as doesn't interact with class
async def handle_tier_claim(tier_type: str, ctx: commands.Context = None,
                            interaction: discord.Interaction = None):
    if ctx is None:
        user = interaction.user
    else:
        user = ctx.author

    result = Database.claim_specific_lootbox(user.id, tier_type)
    if result is None:
        if ctx is None:
            await interaction.response.send_message(f"You have no {tier_type.title()} lootboxes left!",
                                                    ephemeral=True)
        else:
            ctx.send(f"You have no {tier_type.title()} lootboxes left!", ephemeral=True)
        return

    reward = result
    color = Items.LOOT_TIERS[tier_type]["color"]
    embed = discord.Embed(
        title=f"{tier_type.title()} Lootbox Opened!",
        description=f"{user.display_name} received **💰 {reward} ForeCoins**!",
        color=color
    )
    if ctx is None:
        await interaction.response.send_message(embed=embed)
    else:
        await ctx.send(embed=embed)
