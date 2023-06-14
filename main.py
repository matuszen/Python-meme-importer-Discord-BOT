import discord
from discord.ext import commands
from MediaImporter import MediaImporter

TOKEN = ""
CHANNEL_ID = ""

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

    channel = bot.get_channel(int(CHANNEL_ID))

    importer = MediaImporter()

    importer.find_media_urls()

    await importer.import_images(channel)

    await bot.close()


if __name__ == "__main__":
    bot.run(TOKEN)
