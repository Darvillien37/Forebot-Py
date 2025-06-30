from discord.ui import View, Button
import discord
from Database import Database


class LootboxClaimView(View):
    def __init__(self, user_id: int, timeout=60):
        super().__init__(timeout=timeout)
        self.user_id = user_id

        for tier in Database.LOOT_TIERS:
            emoji = Database.LOOT_TIERS[tier]["emoji"]
            label = tier.title()
            button = Button(
                label=label,
                emoji=emoji,
                custom_id=tier,
                style=discord.ButtonStyle.primary
            )
            button.callback = self.make_callback(tier)
            self.add_item(button)

    def make_callback(self, tier):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("You can't claim other users' lootboxes.", ephemeral=True)
                return

            result = Database.claim_specific_lootbox(self.user_id, tier)
            if result is None:
                await interaction.response.send_message(f"You have no {tier.title()} lootboxes left!", ephemeral=True)
                return

            reward = result
            color = Database.LOOT_TIERS[tier]["color"]
            embed = discord.Embed(
                title=f"{tier.title()} Lootbox Opened!",
                description=f"You received **💰 {reward} coins**!",
                color=color
            )
            await interaction.response.send_message(embed=embed)
        return callback
