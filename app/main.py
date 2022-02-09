import logging
from app.bot import MachineElfBot

from app.config import get_settings
from app.anon.cog import AnonCog
from app.suffer.cog import SufferCog
from app.test_cog import TestCog


def setup_logging():
    logging.basicConfig(**get_settings().logging.setup)
    for log_name, level in get_settings().logging.levels.items():
        logging.getLogger(log_name).setLevel(level)


def main():
    setup_logging()

    logging.debug(f"Loaded config:\n{get_settings().json()}")

    bot = MachineElfBot(
        owner_id=get_settings().bot.owner_id,
        test_guilds=get_settings().bot.guilds,
    )

    bot.add_cog(TestCog(bot))
    bot.add_cog(AnonCog(bot))
    bot.add_cog(SufferCog(bot))

    logging.info("Starting bot...")
    bot.run(get_settings().bot.token)


if __name__ == "__main__":
    main()
