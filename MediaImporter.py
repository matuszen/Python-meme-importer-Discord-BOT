import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import discord

WEBSITES = {
    "JBZD": {
        "URL": "https://jbzd.com.pl",
        "MEDIA_URL": "https://i1.jbzd.com.pl"
    }
}

class MediaFilter:
    def __init__(self, media_urls: tuple) -> None:
        self.media_urls = media_urls
    
    def find_media_in_jbzd(self) -> None:
        response = requests.get(WEBSITES["JBZD"]["URL"])
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("article", class_="article")

        for article in articles:
            article_time = article.find("span", class_="article-time")
            posted_time = article_time.get("data-date")
            posted_datetime = datetime.strptime(posted_time, "%Y-%m-%d %H:%M:%S")

            if posted_datetime >= self.last_import_time:
                images = article.find_all("img")
                for image in images:
                    image_url = image.get("src")
                    if (
                        image_url
                        and image_url.startswith(WEBSITES["JBZD"]["MEDIA_URL"])
                        and "/normal/" in image_url
                    ):
                        self.media_urls.add(image_url)

                videos = article.find_all("videoplyr")
                for video in videos:
                    video_url = video.get("video_url")
                    if video_url:
                        self.media_urls.add(video_url)
    

class MediaImporter:
    def __init__(self, temp_media_directory: str = "cache") -> None:
        self.media_urls = set()
        self.temp_media_directory = temp_media_directory

        if not os.path.exists(self.temp_media_directory):
            os.makedirs(self.temp_media_directory)

    def find_media_urls(self) -> None:
        filter = MediaFilter(self.media_urls)

        filter.find_media_in_jbzd()

        self.media_urls = filter.media_urls

    async def import_images(self, channel) -> None:
        for image_url in self.media_urls:
            image_filename = image_url.split("/")[-1]
            image_response = requests.get(image_url, stream=True)
            if image_response.status_code == 200:
                image_path = os.path.join(self.temp_media_directory, image_filename)

                with open(image_path, "wb") as file:
                    for chunk in image_response.iter_content(chunk_size=8192):
                        file.write(chunk)

                discord_file = discord.File(image_path, filename=image_filename)
                await channel.send(file=discord_file)
                os.remove(image_path)

    def set_last_import_time(self, last_import_time):
        self.last_import_time = last_import_time
