import discord
from discord.ext import commands
import logging as log

from .token import TOKEN, CHANNEL_ID
from .MediaImporter import MediaImporter

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready() -> None:
    log.info(f"Succesfully logged in as {bot.user.name}")

    try:
        await bot.fetch_channel(CHANNEL_ID)

    except discord.errors.InvalidData:
        log.error(f"Unknown channel type was received from Discord")
        return

    except discord.errors.NotFound:
        log.error(f"Invalid Channel ID")
        return

    except discord.errors.Forbidden:
        log.error(f"You do not have permission to fetch this channel")
        return

    except discord.errors.HTTPException:
        log.error(f"Retrieving the channel failed")
        return

    channel = bot.get_channel(CHANNEL_ID)

    importer = MediaImporter()
    importer.find_media_urls()

    await importer.import_images(channel)
    await bot.close()


if __name__ == "__main__":
    print()
    bot.run(TOKEN)
    print()
