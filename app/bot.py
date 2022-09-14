import disnake.ext.commands as discord
import disnake

from app.collect.cog import CollectView


class MachineElfBot(discord.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._persistent_views_added = False

    async def on_slash_command_error(
        self,
        event: disnake.ApplicationCommandInteraction,
        exception: discord.errors.CommandError,
    ) -> None:
        await super().on_slash_command_error(event, exception)
        match exception:
            case discord.MissingAnyRole() | discord.MissingRole() | discord.MissingPermissions():
                await event.send(
                    "You don't have sufficient permissions to run that command.",
                    ephemeral=True,
                )

    async def on_ready(self):
        if not self._persistent_views_added:
            self.add_view(CollectView())
            self._persistent_views_added = True
