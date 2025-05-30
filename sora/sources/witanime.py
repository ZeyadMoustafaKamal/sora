from sora.utils import Proxy, base64_decode, get_from_to
from sora.downloaders import MediafireDownloader
from sora.sources.base import BaseEpisode, BaseSource

from bs4 import BeautifulSoup as Bs

import json


class WitAnimeSource(BaseSource):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.episode_class = Episode

    def get_anime_info(self):
        info = {}
        r = self.client.get(self.url)
        soup = Bs(r.text, "lxml")
        soup = Proxy(soup)
        indirect_urls = []
        for ep in soup.find(id="ULEpisodesList").find_all("a"):
            url_encoded = ep.attrs.get("onclick")[13:-2]
            url = base64_decode(url_encoded)
            indirect_urls.append(url)
        if not indirect_urls:
            raise ValueError("An error occured")
        info["indirect_urls"] = indirect_urls
        info["title"] = soup.find(attrs={"class": "anime-page-link"}).find("a").text
        return info

    def get_episodes_urls(self, episodes):
        indirect_urls = self.indirect_urls
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


class Episode(BaseEpisode):
    def get_episode_info(self):
        info = {}
        r = self.client.get(self.url)
        soup = Bs(r.text, "lxml")
        soup = Proxy(soup)
        js_data = soup.find(id="d-l-js-extra")
        urls = self.parse_js_urls(js_data.text)
        title = soup.find_all(attrs={"class": "main-section"})[-1].find("h3").text
        quality_info = self.get_quality_info(r.text)

        info["title"] = title
        info["urls"] = urls
        info["quality"] = quality_info
        return info

    def parse_js_urls(self, js):
        urls_data = json.loads(get_from_to(js, '["', '"]', 2))
        decoded_urls = [base64_decode(url) for url in urls_data]
        offset_data = json.loads(get_from_to(js, "[{", "}]", 2))
        urls = []
        for i, item in enumerate(offset_data):
            decoded_k = int(base64_decode(item["k"]))
            offset = item["d"][decoded_k]
            clean_url = decoded_urls[i][:-offset]
            urls.append(clean_url)
        return urls

    def download(self, qualiy_number):
        quality = self.get_quality_from_number(qualiy_number)
        mediafire = quality.get("mediafire")
        if mediafire:
            url = self.info["urls"][int(mediafire)]
            downloader = MediafireDownloader(url, self.path)
            downloader.download()
        else:
            raise ValueError(
                "Only {} exists which are not suported yet", quality.keys()
            )

    def get_quality_from_number(self, quality_number=None):
        quality_number = quality_number or 2
        quality_order = {1: "SD HD FHD", 2: "HD SD FHD", 3: "FHD HD SD"}.get(
            quality_number
        )

        quality_info = self.info["quality"]

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
        soup = Proxy(soup)
        info = {"SD": {}, "FHD": {}, "HD": {}}
        quality_list = soup.find_all(attrs={"class": "quality-list"})
        if quality_list is None:
            raise ValueError("Couldn't find the video. Wrong url ?")

        for quality_element in quality_list:
            quality_text = quality_element.find("li").text
            for quality_option in info.keys():
                if quality_option in quality_text:
                    info[quality_option] = self.filter_quality(quality_element)
                    break
        return info

    def filter_quality(self, html):
        info = {}
        download_elements = html.find_all(attrs={"class": "download-link"})
        if download_elements is not None:
            for download_element in download_elements:
                quality_text = download_element.find("span").text
                info[quality_text] = download_element.attrs.get("data-index")
        return info
