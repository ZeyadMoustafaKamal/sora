from sora.anime import Episode

import httpx


class BaseSource:
    # The source will simply take the input params (url, path ...etc)
    # have the download method that will download the episode/s.
    def __init__(self, url, path) -> None:
        self.url = url
        self.path = path
        self.client = httpx.Client()
        self.info = self.get_anime_info()

    def get_anime_info(self):
        raise NotImplementedError()

    def get_episodes_urls(self, episodes):
        raise NotImplementedError()

    def download(self, episodes, quality=None):
        quality = quality or 2
        episodes_urls = self.get_episodes_urls(episodes)
        for url in episodes_urls:
            episode = Episode(url, self.path, client=self.client)
            print("Downloading {}".format(episode.info["title"]))
            episode.download(quality)

    @property
    def title(self):
        return self.info["title"]

    @property
    def indirect_urls(self):
        return self.info["indirect_urls"]

    @property
    def episodes_number(self):
        return self.info["episodes_number"]


class BaseEpisode:
    def __init__(self, url, path=None, client=None) -> None:
        self.url = url
        self.path = path
        self.client = client or httpx.Client()
        self.info = self.get_episode_info()

    def get_episode_info(self):
        raise NotImplementedError()

    def download(self, quality_number):
        raise NotImplementedError()
