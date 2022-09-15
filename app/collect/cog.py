import asyncio
import disnake.ext.commands as discord
import disnake
import aiohttp

from app.config import get_settings


class CollectModal(disnake.ui.Modal):
    def __init__(self):
        super().__init__(
            title="Accept & Join",
            components=[
                disnake.ui.TextInput(
                    label="Email",
                    placeholder="john.doe@example.com",
                    custom_id="email",
                    style=disnake.TextInputStyle.short,
                ),
            ],
        )

    async def callback(self, event: disnake.ModalInteraction):
        await event.response.defer(ephemeral=True)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                get_settings().collect.api_url,
                headers={"x-api-key": get_settings().collect.api_key},
                json={
                    "key": event.text_values["email"],
                    "value": f"{event.user.name}#{event.user.tag} ({event.user.display_name})",
                },
            ) as resp:
                await resp.json()
        await event.guild.fetch_roles()
        await asyncio.gather(
            event.user.add_roles(event.guild.get_role(get_settings().collect.role_id)),
            event.followup.send(get_settings().collect.success_message, ephemeral=True),
        )


class CollectView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(
        label="Accept & Join",
        style=disnake.ButtonStyle.green,
        custom_id="collect_button",
    )
    async def collect(
        self, button: disnake.ui.Button, event: disnake.MessageInteraction
    ):
        await event.response.send_modal(CollectModal())


class CollectCog(discord.Cog):
    def __init__(self, bot: discord.Bot, **kwargs):
        self._bot = bot

    @discord.slash_command()
    @discord.has_any_role(*get_settings().bot.admin_roles)
    async def collect(
        self,
        event: disnake.ApplicationCommandInteraction,
    ):
        """
        Create a button to collect Discord usernames.
        """
        await event.response.send_message(view=CollectView())
