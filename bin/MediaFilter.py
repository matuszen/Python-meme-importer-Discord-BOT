import logging
import datetime
import requests

from bs4 import BeautifulSoup, element

log = logging.getLogger("MediaFilter")

WEBSITES = {
    "JBZD": {
        "MAIN_URL": "https://jbzd.com.pl/str/",
        "WAITING_URL": "https://jbzd.com.pl/oczekujace/",
        "MEDIA_URL": "https://i1.jbzd.com.pl",
    },
}


class MediaFilter:
    def __init__(
        self,
        media_urls: set,
        last_import_time: datetime,
    ) -> None:
        self.media_urls: set[str] = media_urls
        self.last_import_time: datetime = last_import_time

    def _get_file_size(self, url: str) -> int | None:
        response: requests.Response = requests.head(url)

        if "Content-Length" in response.headers[0]:
            file_size = int(response.headers["Content-Length"])
            return file_size

    def find_media_in_jbzd(
        self,
        which_page: str = "main",
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
                posted_datetime = datetime.datetime.strptime(
                    posted_time, "%Y-%m-%d %H:%M:%S"
                )

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
                            log.debug(f"Image found: {image_url.split('/')[-1]}")
                            elements_count += 1

                    for video in videos:
                        video_url = video.get("video_url")
                        if video_url:
                            self.media_urls.add(video_url)
                            log.debug(f"Video found: {video_url.split('/')[-1]}")
                            elements_count += 1

                    last_subpage = False

                else:
                    last_subpage = True

            subpage += 1

        log.debug(f"In jbzd.com.pl ({which_page} page), find {elements_count} items")

    def __enter__(self) -> "MediaFilter":
        return self

    def __exit__(self) -> None:
        return None
