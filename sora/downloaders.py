from bs4 import BeautifulSoup as Bs
import httpx

from sora.utils import get_random_name

from gzip import GzipFile
from io import BytesIO
import urllib
import http.client
import os


class BaseDownloader:
    def __init__(self, direct_url, path=None, filename=None):
        self.direct_url = direct_url
        self._path = path
        self.filename = filename

    def download(self):
        pass

    def get_path(self):
        path = self._path or os.getcwd()
        return path

    def get_filename(self):
        return self.filename


class MediafireDownloader(BaseDownloader):
    def download(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Accept-Encoding": "gzip",
        }
        # for some reason, mediafire detects that this is a bot if I used httpx instead of the low level http.client
        parsed_url = urllib.parse.urlparse(self.direct_url)
        conn = http.client.HTTPConnection(parsed_url.netloc)
        conn.request(
            "GET",
            parsed_url.path,
            headers=headers,
        )
        response = conn.getresponse()
        compressed_data = response.read()
        conn.close()
        with GzipFile(fileobj=BytesIO(compressed_data)) as f:
            html = f.read().decode("utf-8")
            soup = Bs(html, "lxml")
            direct_download_url = soup.find("a", {"id": "downloadButton"}).attrs["href"]
            conn = http.client.HTTPConnection(parsed_url.netloc)
            conn.request(
                "GET",
                parsed_url.path,
                headers=headers,
            )
            response = conn.getresponse()

        with httpx.stream("GET", direct_download_url) as r:
            file = open(self.get_path(), "wb")
            for chunk in r.iter_bytes(1024):
                file.write(chunk)
            file.close()

    def get_path(self):
        path = super().get_path()
        filename = self.get_filename()
        return os.path.join(path, filename)

    def get_filename(self):
        filename = super().get_filename()
        if filename:
            return filename

        file_key = self.direct_url.split("/")[4]
        file_info_url = "https://www.mediafire.com/api/file/get_info.php?quick_key={}&response_format=json".format(
            file_key
        )
        r = httpx.get(file_info_url.format(file_key)).json().get("response")
        file_info = r.get("file_info")
        if file_info:
            filename = file_info.get("filename")
            if filename:
                return filename
        if not file_info or not filename:
            filename = get_random_name()
        print("Downloading file: {}".format(filename))
        return filename
