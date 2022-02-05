import asyncio
import disnake.ext.commands as discord
import disnake


class TestCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self._bot = bot

    @discord.slash_command()
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
