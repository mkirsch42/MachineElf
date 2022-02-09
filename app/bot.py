import disnake.ext.commands as discord
import disnake


class MachineElfBot(discord.Bot):
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
