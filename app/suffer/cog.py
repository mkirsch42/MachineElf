import asyncio
import random
from typing import Optional
import disnake.ext.commands as discord
import disnake

from app.suffer.db import SufferStore
from app.config import get_settings


class SufferCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self._bot = bot

    @staticmethod
    def messages():
        return get_settings().suffer.messages

    async def stats_embed(self, store: SufferStore) -> disnake.Embed:
        embed = disnake.Embed(title=self.messages().stats_title)
        counts = await asyncio.gather(
            *[
                store.last_n_days(n) if n > 0 else store.total_count()
                for n in get_settings().suffer.ranges
            ]
        )

        for pos, (n, count) in enumerate(zip(get_settings().suffer.ranges, counts)):
            embed.add_field(
                self.messages().stats_range.format(n)
                if n > 0
                else self.messages().stats_alltime,
                self.messages().stats_count.format(count),
                inline=(
                    get_settings().suffer.embed_inline
                    and not (pos == 0 and get_settings().suffer.embed_first_newline)
                ),
            )
        return embed

    @discord.slash_command()
    async def suffer(self, _):
        ...

    @suffer.sub_command()
    @discord.has_any_role(*get_settings().bot.admin_roles)
    async def increment(
        self,
        event: disnake.ApplicationCommandInteraction,
        count: int = 1,
        message: Optional[str] = None,
        stats: bool = True,
    ):
        """
        Record a substance inquiry.

        Parameters
        ----------
        count: How many events to log. Default 1.
        message: An optional message to attach to the event
        stats: Whether to additionally print recent stats. Default true.
        """
        async with SufferStore(event.guild_id) as store:
            futs = []
            for _ in range(count):
                futs.append(store.put(message=message))
            await asyncio.gather(*futs)

            content = random.choice(self.messages().new_event_options).format(
                "".join(
                    [
                        f"{digit}\u20E3"
                        for digit in str(
                            await store.last_n_days(get_settings().suffer.last_n_days)
                        )
                    ]
                )
            )

            if message:
                content = f"{content}\n{message}"

            if stats:
                await event.send(content, embed=await self.stats_embed(store))
            else:
                await event.send(content)

    @suffer.sub_command()
    async def stats(
        self,
        event: disnake.ApplicationCommandInteraction,
    ):
        """
        Print out stats for recent substance inquiries.
        """
        async with SufferStore(event.guild_id) as store:
            await event.send(embed=await self.stats_embed(store))
