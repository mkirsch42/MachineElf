import asyncio
from typing import Dict
import disnake.ext.commands as discord
import disnake

from app.anon.store import AnonStore
from app.config import get_settings


class AnonCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self._bot = bot
        self._anons = AnonStore()

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
        anon_user = self._anons[event.author]
        newid = newid or event.channel not in anon_user
        anon = anon_user[event.channel]
        reply = get_settings().anon.messages.sending

        if newid or anon.expired:
            anon.new_id()
            reply = get_settings().anon.messages.new_id

        await event.send(reply.format(anon.id), ephemeral=True)

        if not anon.hook:
            anon.hook = await event.channel.create_webhook(
                name=f"anon-{anon.id}", avatar=anon.icon
            )
        await anon.hook.send(
            message, username=get_settings().anon.messages.username.format(anon.id)
        )
