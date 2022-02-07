import disnake.ext.commands as discord
import disnake

from app.anon.store import AnonStore
from app.config import get_settings


class AnonCog(discord.Cog):
    def __init__(self, bot: discord.Bot, **kwargs):
        self._bot = bot
        self._store = AnonStore(**kwargs)

    @discord.slash_command()
    async def anon(
        self,
        event: disnake.ApplicationCommandInteraction,
        message: str,
        newid: bool = False,
    ):
        """
        Send an anonymous message. IDs will be deleted after 30 minutes of inactivity.

        Parameters
        ----------
        message: The message to anonymously send
        newid: Force a new id to be generated for this channel
        """
        if get_settings().anon.defer:
            await event.response.defer(ephemeral=True)
        reply = get_settings().anon.messages.sending
        path = (event.author.id, event.channel.id)

        if newid:
            id_created = True
            anon_id, icon = await self._store.create_id(path)
        else:
            anon_id, icon, id_created = await self._store[path]

        if id_created:
            reply = get_settings().anon.messages.new_id

        await event.send(reply.format(anon_id), ephemeral=True)
        hook = await event.channel.create_webhook(name=f"anon-{anon_id}", avatar=icon)
        await hook.send(
            message, username=get_settings().anon.messages.username.format(anon_id)
        )
        await hook.delete()
