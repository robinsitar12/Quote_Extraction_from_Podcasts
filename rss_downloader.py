"""
Handles fetching a podcast's RSS feed and downloading episode mp3 files into a local directory for further processing.
My code is mainly based on the code of Hojiakbar Barotov (source: https://medium.com/@hmbarotov/asynchronous-podcast-downloader-with-python-a26f2ffff98a)
"""

import os
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential


class Podcast:
    """
    Fetches episodes from a podcast RSS feed and downloads them as mp3 files.
    """

    def __init__(self, url: str, mp3_folder: str):
        """
        Args:
            url: RSS feed URL.
            mp3_folder: Folder where downloaded mp3 files are stored.
        """
        self.url = url
        self.mp3_folder = mp3_folder
        os.makedirs(self.mp3_folder, exist_ok=True)

    def get_episodes(self, limit: int):
        """
        Fetch and parse podcast episodes from the RSS feed.

        Args:
            limit: Maximum number of episodes to fetch.

        Returns:
            A list of BeautifulSoup Tag objects, one per episode.
        """
        response = requests.get(self.url)
        response.raise_for_status()  # raises if the feed URL is invalid
        soup = BeautifulSoup(response.content, "xml")
        return soup.find_all("item", limit=limit)

    @staticmethod
    def to_filename(string: str) -> str:
        """
        Sanitize a string into a valid filename by stripping characters that
        are illegal in Windows/macOS/Linux filenames.

        Args:
            string: Raw episode (or podcast) title.

        Returns:
            A filename-safe string with only alphanumerics and " -_.#&" allowed.
        """
        return "".join(c for c in string if c.isalnum() or c in " -_.#&").strip()

    def download_episode(self, item) -> tuple[str, str]:
        """
        Download a single episode and save it as an mp3 file.

        Args:
            item: A BeautifulSoup Tag object representing one RSS <item>.

        Returns:
            A tuple of (episode_title, mp3_file_path).
        """

        @retry(
            stop=stop_after_attempt(5),
            wait=wait_exponential(multiplier=1, min=2, max=32), # just in case network or website temporarily crashes/overloads to not break the whole code processing
        )
        def _download():
            with requests.get(mp3_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):  # avoid loading whole file into RAM
                        if chunk:  # filter out keep-alive chunks
                            f.write(chunk)

        title = item.find("title").text
        mp3_url = item.find("enclosure")["url"]
        file_name = self.to_filename(title)
        file_path = os.path.join(self.mp3_folder, f"{file_name}.mp3")

        _download()

        return title, file_path
