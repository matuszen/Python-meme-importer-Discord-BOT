import os
import requests
from bs4 import element, BeautifulSoup
from datetime import datetime
import discord
import pickle

TEMP_MEDIA_DIRECTORY_NAME = "cache"
LAST_IMPORT_TIME_FILE = "last_run_time.pkl"

WEBSITES = {
    "JBZD": {
        "MAIN_URL": "https://jbzd.com.pl/str/",
        "WAITING_URL": "https://jbzd.com.pl/oczekujace/",
        "MEDIA_URL": "https://i1.jbzd.com.pl",
    },
}


class MediaFilter:
    def __init__(self, media_urls: set, last_import_time: datetime) -> None:
        self.media_urls = media_urls
        self.last_import_time = last_import_time

    def _get_file_size(self, url: str) -> int | None:
        response = requests.head(url)

        if "Content-Length" in response.headers:
            file_size = int(response.headers["Content-Length"])
            return file_size

        return None

    def find_media_in_jbzd(
        self, which_page: str = "main", log_info: bool = False
    ) -> None:
        subpage = 1
        elements_count = 0
        last_subpage = False
        should_continue = True

        while should_continue:
            if last_subpage:
                should_continue = False

            URL = f"{WEBSITES['JBZD'][f'{which_page.upper()}_URL']}{subpage}"
            MEDIA_URL = WEBSITES["JBZD"]["MEDIA_URL"]

            response = requests.get(URL)

            soup = BeautifulSoup(response.text, "html.parser")
            articles: list[element.Tag] = soup.find_all("article", class_="article")

            for article in articles:
                article_time = article.find("span", class_="article-time")
                posted_time = article_time.get("data-date")
                posted_datetime = datetime.strptime(posted_time, "%Y-%m-%d %H:%M:%S")

                if posted_datetime >= self.last_import_time:
                    images: list[element.Tag] = article.find_all("img")
                    videos: list[element.Tag] = article.find_all("videoplyr")

                    for image in images:
                        image_url = image.get("src")
                        if (
                            image_url
                            and image_url.startswith(MEDIA_URL)
                            and "/normal/" in image_url
                        ):
                            self.media_urls.add(image_url)
                            if log_info:
                                print(f"Image finded: {image_url.split('/')[-1]}")
                            elements_count += 1

                    for video in videos:
                        video_url = video.get("video_url")
                        if video_url:
                            self.media_urls.add(video_url)
                            if log_info:
                                print(f"Video finded: {video_url.split('/')[-1]}")
                            elements_count += 1

                    last_subpage = False

                else:
                    last_subpage = True

            subpage += 1

        if log_info:
            print(
                f"From jbzd.com.pl ({which_page} page), import: {elements_count} items"
            )


class MediaImporter:
    def __init__(self) -> None:
        self.media_urls = set()
        self.temp_media_directory = TEMP_MEDIA_DIRECTORY_NAME

        if not os.path.exists(self.temp_media_directory):
            os.makedirs(self.temp_media_directory)

        if os.path.exists(f"data\\{LAST_IMPORT_TIME_FILE}"):
            with open(f"data\\{LAST_IMPORT_TIME_FILE}", "rb") as file:
                self.last_import_time: datetime = pickle.load(file)
        else:
            if not os.path.exists("data\\"):
                os.mkdir("data")

            now = datetime.now()
            self.last_import_time = datetime(now.year, now.month, now.day, 0, 0, 0)

    def __del__(self) -> None:
        with open(f"data\\{LAST_IMPORT_TIME_FILE}", "wb") as file:
            now = datetime.now()
            pickle.dump(
                datetime(
                    now.year, now.month, now.day, now.hour, now.minute, now.second
                ),
                file,
            )

    def find_media_urls(self) -> None:
        filter = MediaFilter(self.media_urls, self.last_import_time)

        filter.find_media_in_jbzd(which_page="waiting", log_info=True)

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
