import logging
import discord

from discord.ext import commands

from discord_token import TOKEN, CHANNEL_ID
from MediaImporter import MediaImporter

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
        discord.errors.InvalidData,
        discord.errors.NotFound,
        discord.errors.Forbidden,
        discord.errors.HTTPException,
    ) as e:
        log.error(f"Error during fetching channel: {e}")
        return

    with MediaImporter() as importer:
        importer.find_media_urls()
        with bot.get_channel(CHANNEL_ID) as channel:
            await importer.import_images(channel)

    await bot.close()


if __name__ == "__main__":
    print()
    bot.run(TOKEN)
    print()
