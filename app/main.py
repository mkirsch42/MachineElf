import logging
import disnake.ext.commands as discord

from app.config import get_settings
from app.test_cog import TestCog


def main():
    logging.info("Starting...")
    logging.getLogger("disnake").setLevel(logging.INFO)

    bot = discord.Bot(
        owner_id=get_settings().bot.owner_id,
        test_guilds=get_settings().bot.guilds,
    )

    bot.add_cog(TestCog(bot))

    bot.run(get_settings().bot.token)


main()
