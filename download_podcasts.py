import concurrent.futures
import os
import time

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm


class Podcast:
    ''' 
    Download podcast episodes from an RSS feed
    
    Class attributes:
        PODCAST_URL: RSS feed URL of podcast to scrape
        PODCAST_NAME: Used as the download folder name
        PODCASTS_TO_DOWNLOAD: Number of episodes to fetch from the feed asynchronolously
    '''
    
    PODCAST_URL = 'https://feeds.megaphone.fm/SIXMSB5088139739' 
    PODCAST_NAME ='Modern Wisdom'
    PODCASTS_TO_DOWNLOAD = 10

    def __init__(self, url, name):
        '''
        Args:
            url: RSS feed URL.
            name: Podcast name, used to create the download folder
        '''
        self.url = url
        self.folder = os.path.join(os.getcwd(), name)
    
    
    def setup_folder(self, folder=PODCAST_NAME):
        '''
        Create the download folder if it doesn't already exist.
        '''
        os.makedirs(self.folder, exist_ok=True)
      
      
    def get_episodes(self, limit = PODCASTS_TO_DOWNLOAD):
        '''
        Fetch and parse podcast episodes from the RSS feed.
         
        Args:
            limit: maximum number of podcast episodes to download
            
        Returns:
            A list of BeautifulSoup Tag objects, one per episode.
        '''
        
        response = requests.get(self.url)
        response.raise_for_status() # safety check if URL does exist or raises errors
        soup = BeautifulSoup(response.content, 'xml') # use xml parser to analyze rss feeds
        return soup.find_all('item', limit = limit) # finds all podcast episodes stores in the 'item' objects
    
    
    def to_filename(self, string):
        '''
        Sanitize a string into a valid filename by stripping illegal characters for OS operating system
        
        Args:
            string: Raw episode title
            
        Result:
            a filename-safe string with only alphanumerics and ' -_.#&' allowed.
        '''
        return "".join(c for c in string if c.isalnum() or c in " -_.#&").strip() # check characters for allowed format and remove whitespace using strip()
    
    
    def download_episodes(self, item):
        '''
        Download a single episode and save it as an MP3
        
        Args:
            item: a BeautifulSoup Tag object representing an RSS item
        
        Returns:
            A summary string with the filename and size e.g., '#001 - Title (45.2 MB)
        '''
        
        @retry(
            stop = stop_after_attempt(5),
            wait = wait_exponential(multiplier = 1, min = 2, max = 32)
        )
        
    
        def _download():
            with requests.get(mp3_url, stream = True, timeout = 30) as r:
                r.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size = 8192): # avoid RAM overload
                        if chunk: # empty chunks will be ignored
                            f.write(chunk)
    
        title = item.find('title').text
        mp3_url = item.find('enclosure')['url'] # find url to download mp3 file
        mp3_size_mb = round(int(item.find('enclosure')['length']) / 1024**2, 2) 
        file_name = self.to_filename(title)
        file_path = os.path.join(self.folder, f"{file_name}.mp3")
        
        _download()
        
        return f'{file_name} ({mp3_size_mb} MB)'