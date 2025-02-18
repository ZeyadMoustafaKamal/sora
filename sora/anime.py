import httpx
from bs4 import BeautifulSoup as Bs

from sora.downloaders import MediafireDownloader
from sora.utils import get_from_to

import base64
import json


class Anime:
    def __init__(self, url) -> None:
        self.url = url
        self.client = httpx.Client()
        self.info = self.get_anime_info()

    def get_anime_info(self):
        info = {}
        r = self.client.get(self.url)
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

    def download(self, episode_line, quality=None):
        if quality is None:
            quality = 2
        episodes_urls = self.get_episodes_urls(episode_line)
        for url in episodes_urls:
            episode = Episode(url, self.client)
            print("downloading {}".format(episode.info["title"]))
            episode.download(quality)

    def get_episodes_urls(self, episodes):
        indirect_urls = self.info["indirect_urls"]
        if episodes == "all":
            print("Downloading all the {} episodes".format(len(indirect_urls)))
            return indirect_urls
        if "-" not in episodes:
            episodes = int(episodes)
            print("Downloading episode number {}".format(episodes))
            return [indirect_urls[episodes - 1]]
        start, end = episodes.split("-")
        start, end = int(start), int(end)
        print("downloading from {} to {}".format(start, end))
        return indirect_urls[start - 1 : end]

    @property
    def indirect_urls(self):
        return self.info["indirect_urls"]


class Episode:
    def __init__(self, url, client=None) -> None:
        self.url = url
        self.client = client or httpx.Client()
        self.info = self.get_episode_info()

    def get_episode_info(self):
        info = {}
        r = self.client.get(self.url)
        soup = Bs(r.text, "lxml")
        js_data = soup.find(id="d-l-js-extra")
        urls = self.parse_js_urls(js_data.text)
        title = soup.find_all(attrs={"class": "main-section"})[-1].find("h3").text
        quality_info = self.get_quality_info(r.text)

        info["title"] = title
        info["url"] = urls
        info["quality"] = quality_info
        return info

    def parse_js_urls(self, js):
        urls_data = json.loads(get_from_to(js, '["', '"]', 2))
        decoded_urls = [base64.b64decode(url).decode("utf-8") for url in urls_data]
        offset_data = json.loads(get_from_to(js, "[{", "}]", 2))
        urls = []
        for i, item in enumerate(offset_data):
            decoded_k = int(base64.b64decode(item["k"]).decode("utf-8"))
            offset = item["d"][decoded_k]
            clean_url = decoded_urls[i][:-offset]
            urls.append(clean_url)
        return urls

    def download(self, qualiy_number):
        quality = self.get_quality_from_number(qualiy_number)
        mediafire = quality.get("mediafire")
        if mediafire:
            url = self.info["url"][int(mediafire)]
            downloader = MediafireDownloader(url)
            downloader.download()
        else:
            raise ValueError(
                "Only {} exists which are not suported yet", quality.keys()
            )

    def get_quality_from_number(self, quality_number=None):
        if quality_number is None:
            quality_number = 2
        quality_info = self.info["quality"]
        if quality_number == 1:
            quality_order = "SD HD FHD"
        elif quality_number == 2:
            quality_order = "HD SD FHD"
        elif quality_number == 3:
            quality_order = "FHD HD SD"
        for quality in quality_order.split():
            if quality_info[quality]:
                return quality_info[quality]
        raise ValueError("Couldn't process quality info.")

    def get_quality_info(self, html):
        """
        Return all evailable quality options along with their data-index that can be used
        to get the direct link of the episode.
        """
        soup = Bs(html, "lxml")
        info = {"SD": {}, "HD": {}, "FHD": {}}
        quality_list = soup.find_all(attrs={"class": "quality-list"})
        if quality_list is not None:
            for quality_element in quality_list:
                quality_text = quality_element.find("li").text
                if "SD" in quality_text:
                    info["SD"] = self.filter_quality(quality_element)
                elif "FHD" in quality_text:
                    info["FHD"] = self.filter_quality(quality_element)

                elif "HD" in quality_text:
                    info["HD"] = self.filter_quality(quality_element)

                else:
                    raise ValueError(
                        "An error occured while processing the quality info. Try again later"
                    )
            return info
        raise ValueError("Couldn't find the video. Wrong url ?")

    def filter_quality(self, html):
        info = {}
        download_elements = html.find_all(attrs={"class": "download-link"})
        if download_elements is not None:
            for download_element in download_elements:
                quality_text = download_element.find("span").text
                info[quality_text] = download_element.attrs.get("data-index")
        return info
