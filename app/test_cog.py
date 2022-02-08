import asyncio
import disnake.ext.commands as discord
import disnake

from app.config import get_settings


class TestCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self._bot = bot

    @discord.slash_command(guild_ids=get_settings().test.guilds)
    async def test(self, _):
        """Test Commands"""

    @test.sub_command()
    async def ping(
        self,
        event: disnake.ApplicationCommandInteraction,
        message: str = "Pong!",
        wait: float = 0.0,
    ):
        """
        Replies Pong!

        Parameters
        ----------
        message: the message to reply with
        wait: the number of seconds to wait before replying
        """
        if wait > 0:
            await event.response.defer(ephemeral=True)
            async with event.channel.typing():
                await asyncio.sleep(wait)

        await event.send(message, ephemeral=True)

    @test.sub_command()
    async def flush_webhooks(
        self, event: disnake.ApplicationCommandInteraction, allguilds: bool = False
    ):
        futs = []
        await event.response.defer()
        for guild in event.bot.guilds if allguilds else [event.guild]:
            for wh in await guild.webhooks():
                futs.append(wh.delete(reason="/flush_webhooks"))
        await asyncio.gather(*futs)
        await event.send(f"Done! Flushed {len(futs)} webhooks.")
