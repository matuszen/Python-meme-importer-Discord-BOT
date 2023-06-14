import os
import requests
import discord
from bs4 import BeautifulSoup
from discord.ext import commands
from datetime import datetime

TOKEN = ""
CHANNEL_ID = ""
WEBPAGE_URL = "https://jbzd.com.pl"
SUBDOMAIN = "https://i1.jbzd.com.pl"

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)

IMAGES_DIRECTORY = "cache"


class MediaImporter:
    def __init__(self, webpage_url, subdomain):
        self.webpage_url = webpage_url
        self.subdomain = subdomain
        self.media_urls = set()

    def find_media_urls(self):
        response = requests.get(self.webpage_url)
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("article", class_="article")

        for article in articles:
            article_time = article.find("span", class_="article-time")
            posted_time = article_time.get("data-date")
            posted_datetime = datetime.strptime(posted_time, "%Y-%m-%d %H:%M:%S")

            print(posted_time)

            if posted_datetime >= self.last_import_time:
                images = article.find_all("img")
                for image in images:
                    image_url = image.get("src")
                    if (
                        image_url
                        and image_url.startswith(self.subdomain)
                        and "/normal/" in image_url
                    ):
                        print(image_url)
                        self.media_urls.add(image_url)

                videos = article.find_all("videoplyr")
                for video in videos:
                    video_url = video.get("video_url")
                    if video_url:
                        self.media_urls.add(video_url)

    async def import_images(self, channel):
        for image_url in self.media_urls:
            image_filename = image_url.split("/")[-1]
            image_response = requests.get(image_url, stream=True)
            if image_response.status_code == 200:
                image_path = os.path.join(IMAGES_DIRECTORY, image_filename)

                with open(image_path, "wb") as file:
                    for chunk in image_response.iter_content(chunk_size=8192):
                        file.write(chunk)

                discord_file = discord.File(image_path, filename=image_filename)
                await channel.send(file=discord_file)
                os.remove(image_path)

    def set_last_import_time(self, last_import_time):
        self.last_import_time = last_import_time


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

    channel = bot.get_channel(int(CHANNEL_ID))

    if not os.path.exists(IMAGES_DIRECTORY):
        os.makedirs(IMAGES_DIRECTORY)

    importer = MediaImporter(WEBPAGE_URL, SUBDOMAIN)

    last_import_time = datetime(2023, 6, 14, 0, 0, 0)

    importer.set_last_import_time(last_import_time)

    importer.find_media_urls()
    await importer.import_images(channel)

    await bot.close()


bot.run(TOKEN)
