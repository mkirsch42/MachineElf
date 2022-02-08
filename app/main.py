import logging
import disnake.ext.commands as discord
from app.anon import AnonCog

from app.config import get_settings
from app.test_cog import TestCog


def setup_logging():
    logging.basicConfig(**get_settings().logging.setup)
    for log_name, level in get_settings().logging.levels.items():
        logging.getLogger(log_name).setLevel(level)


def main():
    setup_logging()

    logging.debug(f"Loaded config:\n{get_settings().json()}")

    bot = discord.Bot(
        owner_id=get_settings().bot.owner_id,
        test_guilds=get_settings().bot.guilds,
    )

    bot.add_cog(TestCog(bot))
    bot.add_cog(AnonCog(bot))

    logging.info("Starting bot...")
    bot.run(get_settings().bot.token)


if __name__ == "__main__":
    main()
