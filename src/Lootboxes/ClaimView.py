from discord.ui import View, Button
import discord
from Database import Database
from Lootboxes import HandleTierClaim
# from Lootboxes.Lootboxes import Lootboxes


class LootboxClaimView(View):
    def __init__(self, bot, user_id: int, boxes, cog_ref, original_embed: discord.Embed,
                 original_message: discord.Message):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.box_counts = boxes
        self.cog_ref = cog_ref
        self.original_embed = original_embed
        self.original_message = original_message
        for tier in self.box_counts:
            if self.box_counts[tier] > 0:
                self.add_item(self.make_button(tier))

    async def on_timeout(self):
        self.clear_items()
        if self.original_message is not None:
            await self.original_message.edit(view=self)

    def make_button(self, tier):
        emoji = Database.LOOT_TIERS[tier]["emoji"]
        label = f"{emoji} {tier.title()}"
        # colour = Database.LOOT_TIERS[tier]["color"]

        # Convert color to ButtonStyle
        style = discord.ButtonStyle.primary
        button = Button(label=label, style=style)

        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Not your lootbox!", ephemeral=True)
                return

            await HandleTierClaim.handle_tier_claim(tier, None, interaction)

            # Update counts after claim
            self.box_counts[tier] -= 1
            if self.box_counts[tier] <= 0:
                self.remove_item(button)

            # Update original embed
            index = 0
            for field in self.original_embed.fields:
                if tier.lower() == field.name.split()[1].strip().lower():
                    self.original_embed.set_field_at(index,
                                                     name=field.name,
                                                     value=self.box_counts[tier])
                index += 1

            await self.original_message.edit(embed=self.original_embed, view=self)

        button.callback = callback
        return button
