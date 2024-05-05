import os
import pickle
import logging
import discord
import requests

from datetime import datetime
from MediaFilter import MediaFilter

LAST_IMPORT_TIME_FILE = "../data/last_run_time.pkl"

log = logging.getLogger("MediaImporter")


class MediaImporter:
    def __init__(self) -> None:
        self.media_urls = set()

        if not os.path.exists("..\\cache"):
            os.makedirs("..\\cache")

        if os.path.exists(f"..\\data\\{LAST_IMPORT_TIME_FILE}"):
            with open(f"..\\data\\{LAST_IMPORT_TIME_FILE}", "rb") as file:
                self.last_import_time: datetime = pickle.load(file)
        else:
            if not os.path.exists("..\\data\\"):
                os.mkdir("..\\data")

            now = datetime.now()
            self.last_import_time = datetime(now.year, now.month, now.day, 0, 0, 0)

    def __enter__(self) -> "MediaImporter":
        return self

    def __exit__(self) -> None:
        with open(f"..\\data\\{LAST_IMPORT_TIME_FILE}", "wb") as file:
            now = datetime.now()
            pickle.dump(
                datetime(
                    now.year, now.month, now.day, now.hour, now.minute, now.second
                ),
                file,
            )
        self._clear_cache()

    def find_media_urls(self) -> None:
        with MediaFilter(self.media_urls, self.last_import_time) as filter:
            filter.find_media_in_jbzd(which_page="waiting")
            self.media_urls = filter.media_urls

    def _clear_cache(self) -> None:
        for file in os.listdir("..\\cache"):
            os.remove(f"..\\cache\\{file}")
        os.rmdir("..\\cache")

    async def import_images(self, channel: discord.Thread) -> None:
        for image_url in self.media_urls:
            image_filename = image_url.split("/")[-1]
            image_response = requests.get(image_url, stream=True)

            if image_response.status_code == 200:
                image_path = os.path.join("..\\cache", image_filename)

                with open(image_path, "wb") as file:
                    for chunk in image_response.iter_content(chunk_size=8192):
                        file.write(chunk)

                discord_file = discord.File(image_path, filename=image_filename)

                try:
                    await channel.send(file=discord_file)

                except discord.errors.HTTPException:
                    log.warning(f"{image_filename} file is to large")

                except discord.errors.ConnectionClosed:
                    log.error("Shard ID None WebSocket closed with 1000")

                except Exception:
                    try:
                        await channel.send(file=discord_file, timeout=3.0)
                    except Exception:
                        log.error(f"Problem with importing {image_filename}")

                os.remove(image_path)

        self._clear_cache()
