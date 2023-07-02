import discord
from bin.utility import log
from discord.ext import commands
from bin.MediaImporter import MediaImporter

TOKEN = ""
CHANNEL_ID = 0

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready() -> None:
    log(f"Succesfully logged in as {bot.user.name}", message_type="info")

    try:
        await bot.fetch_channel(CHANNEL_ID)

    except discord.errors.InvalidData:
        log(f"Unknown channel type was received from Discord", message_type="error")
        return

    except discord.errors.NotFound:
        log(f"Invalid Channel ID", message_type="error")
        return

    except discord.errors.Forbidden:
        log(f"You do not have permission to fetch this channel", message_type="error")
        return

    except discord.errors.HTTPException:
        log(f"Retrieving the channel failed", message_type="error")
        return

    else:
        channel = bot.get_channel(CHANNEL_ID)

    importer = MediaImporter()
    importer.find_media_urls()

    await importer.import_images(channel)
    await bot.close()


if __name__ == "__main__":
    print()
    bot.run(TOKEN)
    print()
