from discord.ui import View, Button
import discord

from Database import Database, attributes


class AttributeUpgradeView(View):
    def __init__(self, bot,
                 member: discord.Member,
                 attr_dict,
                 original_embed: discord.Embed,
                 original_message: discord.Message,
                 show_tips: bool):
        super().__init__(timeout=120)
        self.bot = bot
        self.member = member
        self.attr_dict = attr_dict
        self.original_embed = original_embed
        self.original_message = original_message
        self.show_tips = show_tips

        if attr_dict[attributes.ATTR_UNSPENT_POINTS] > 0:
            for attr in attributes.ATTR_LIST:
                self.add_item(self.make_attribute_button(attr))

    async def on_timeout(self):
        self.clear_items()
        if self.original_message is not None:
            await self.original_message.edit(view=self)

    def make_attribute_button(self, attribute):
        label = f"+1 {attributes.ATTR_LIST[attribute]['emoji']} {attribute.title()}"
        button = Button(label=label, style=discord.ButtonStyle.primary)

        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.member.id:
                await interaction.response.send_message("❌ Not your button!", ephemeral=True)
                return
            await interaction.response.defer()

            Database.increase_attribute(self.member.id, attribute)
            self.attr_dict[attribute] += 1
            self.attr_dict[attributes.ATTR_UNSPENT_POINTS] -= 1

            await self.original_message.edit(embed=attributes.build_attribute_embed(self.member, self.attr_dict, self.show_tips))

            if self.attr_dict[attributes.ATTR_UNSPENT_POINTS] <= 0:
                self.clear_items()
                await self.original_message.edit(view=self)

        button.callback = callback
        return button
