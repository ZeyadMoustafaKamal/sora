import httpx
from bs4 import BeautifulSoup as Bs

from downloaders import MediafireDownloader
from utils import get_from_to

import base64
import json


class Anime:
    def __init__(self, url) -> None:
        self.url = url
        self.info = self.get_anime_info()

    def get_anime_info(self):
        info = {}
        r = httpx.get(self.url)
        soup = Bs(r.text, "lxml")
        indirect_urls = []
        for ep in soup.find(id="ULEpisodesList").find_all("a"):
            url_encoded = ep.attrs.get("onclick")[13:-2]
            url = base64.b64decode(url_encoded).decode("utf-8")
            indirect_urls.append(url)
        if not indirect_urls:
            raise ValueError("An error occured")
        info["indirect_urls"] = indirect_urls
        info["title"] = soup.find(attrs={"class": "anime-page-link"}).find("a").text
        return info

    def download(self, episode_line):
        episodes_urls = self.get_episodes_urls(episode_line)
        for url in episodes_urls:
            episode = Episode(url)
            print("downloading {}".format(episode.info["title"]))
            episode.download()

    def get_episodes_urls(self, episode_line):
        indirect_urls = self.info["indirect_urls"]
        if "-" not in episode_line:
            episode_line = int(episode_line)
            return [indirect_urls[episode_line - 1]]
        start, end = episode_line.split("-")
        start, end = int(start), int(end)
        print("downloading from {} to {}".format(start, end))
        return indirect_urls[start - 1 : end - 1]

    @property
    def indirect_urls(self):
        return self.info["indirect_urls"]


class Episode:
    def __init__(self, url) -> None:
        self.url = url
        self.info = self.get_episode_info()

    def get_episode_info(self):
        info = {}
        r = httpx.get(self.url)
        soup = Bs(r.text, "lxml")
        js_data = soup.find(id="d-l-js-extra")
        urls = self.parse_js_urls(js_data.text)
        media_fire_url = urls[5]  # TODO: allow users to choose the quality
        title = soup.find_all(attrs={"class": "main-section"})[-1].find("h3").text

        info["mediafire_url"] = media_fire_url
        info["title"] = title
        return info

    def parse_js_urls(self, js_data):
        urls_data = json.loads(get_from_to(js_data, '["', '"]', 2))
        decoded_urls = [base64.b64decode(url).decode("utf-8") for url in urls_data]
        offset_data = json.loads(get_from_to(js_data, "[{", "}]", 2))
        urls = []
        for i, item in enumerate(offset_data):
            decoded_k = int(base64.b64decode(item["k"]).decode("utf-8"))
            offset = item["d"][decoded_k]
            clean_url = decoded_urls[i][:-offset]
            urls.append(clean_url)
        return urls

    def download(self):
        medifire_url = self.info["mediafire_url"]
        downloader = MediafireDownloader(medifire_url)
        downloader.download()
