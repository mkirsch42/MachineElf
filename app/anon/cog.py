import asyncio
from typing import Awaitable, List
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
        if get_settings().anon.defer:
            await event.response.defer(ephemeral=True)
        reply = get_settings().anon.messages.sending
        futs: List[Awaitable] = []

        user_anons = self._anons[event.author]
        if (
            newid
            or (event.channel not in user_anons)
            or (user_anons[event.channel].expired)
        ):
            if event.channel in user_anons:
                futs.append(user_anons.delete(event.channel))
            reply = get_settings().anon.messages.new_id

        anon = user_anons[event.channel]
        anon.touch()
        futs.append(event.send(reply.format(anon.id), ephemeral=True))

        await asyncio.gather(*futs)

        if not anon.hook:
            anon.hook = await event.channel.create_webhook(
                name=f"anon-{anon.id}", avatar=anon.icon
            )

        await anon.hook.send(
            message, username=get_settings().anon.messages.username.format(anon.id)
        )
        anon.touch()
