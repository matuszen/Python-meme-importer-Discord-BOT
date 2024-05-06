import logging
import discord

from discord.ext import commands

from discord_token import TOKEN, CHANNEL_ID
from MediaImporter import MediaImporter

from utils import setup_logging

setup_logging(level=logging.INFO)
log = logging.getLogger()

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready() -> None:
    log.info(f"Successfully logged in as {bot.user.name}")

    try:
        await bot.fetch_channel(CHANNEL_ID)

    except (
        discord.errors.NotFound,
        discord.errors.Forbidden,
        discord.errors.InvalidData,
        discord.errors.HTTPException,
    ) as e:
        log.error(f"Error during fetching channel: {e}")
        return

    importer = MediaImporter()
    importer.find_media_urls()

    channel = bot.get_channel(CHANNEL_ID)
    await importer.import_images(channel)

    await bot.close()


if __name__ == "__main__":
    print()

    bot.run(TOKEN, log_handler=None)

    print()
