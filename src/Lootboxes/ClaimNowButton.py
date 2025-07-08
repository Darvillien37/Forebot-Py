import discord
from discord.ui import View, Button
from Lootboxes import Lootboxes


class ClaimNowButton(View):
    def __init__(self, user_id, tier, original_msg: discord.Message, timeout=60):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.tier = tier
        self.original_message = original_msg

        self.add_item(self.make_button(self.tier))

    async def on_timeout(self):
        self.clear_items()
        if self.original_message is not None:
            await self.original_message.edit(view=self)

    def make_button(self, claim_type):
        label = f"Claim {claim_type.title()} Lootbox 🎁"
        button = Button(label=label, style=discord.ButtonStyle.success)

        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Not your lootbox!", ephemeral=True)
                return

            await Lootboxes.handle_tier_claim(self.tier, None, interaction)
            self.remove_item(button)
            await self.original_message.edit(view=self)

        button.callback = callback
        return button
