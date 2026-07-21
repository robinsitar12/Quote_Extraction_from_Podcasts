"""
Entry point for the podcast quote extraction pipeline.

Running this file (python main.py) will:
1. Ask you for a podcast RSS feed URL, the name of the podcast, and how many episodes you want to download (max 5).
2. Ask for your Gemini API key (input is hidden, nothing is saved to disk).
3. Download the episodes as mp3 files (in parallel).
4. Convert each mp3 to wav.
5. Transcribe each wav to text.
6. Use Gemini to extract quotes from each transcript.
7. Print all quotes, tagged with their episode, to the console.

Folders are created automatically next to this file:
    <podcast name>/MP3/
    <podcast name>/WAV/
    <podcast name>/TXT/

The pipeline runs in four separate stages (download -> convert -> transcribe
-> extract quotes) rather than one loop that does all four steps per
episode. This means every episode finishes one stage before the next stage
starts, so the console always shows which stage the whole run is currently in.
"""

import os
import time
import concurrent.futures
from getpass import getpass
from google import genai
from tqdm import tqdm

from config import MAX_EPISODES, MP3_SUBFOLDER, WAV_SUBFOLDER, TXT_SUBFOLDER
from rss_downloader import Podcast
from mp3_to_wav import convert_mp3_to_wav
from wav_to_txt import transcribe_wav_to_text
from quote_extractor import extract_quotes_from_episode


def get_user_settings() -> tuple[str, str, int]:
    """
    Ask the user for the RSS feed URL, podcast name, and number of episodes.

    Returns:
        A tuple of (rss_url, podcast_name, num_episodes).
    """
    rss_url = input("Please insert the podcast RSS feed URL: ").strip()
    podcast_name = input("Podcast name (used as the folder name): ").strip()

    while True:
        raw = input(f"How many episodes do you want to process (1-{MAX_EPISODES}): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= MAX_EPISODES:
            num_episodes = int(raw)
            break
        print(f"Please enter a number between 1 and {MAX_EPISODES}.")

    return rss_url, podcast_name, num_episodes


def download_all_episodes(podcast: Podcast, episodes: list) -> dict:
    """
    Downloads all episodes in parallel.

    Args:
        podcast: A Podcast instance.
        episodes: List of RSS <item> tags to download.

    Returns:
        A dict mapping episode title -> downloaded mp3 file path.
    """
    print("\nStep 1/4: Downloading episodes...")
    mp3_paths = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(podcast.download_episode, item): item for item in episodes}
        with tqdm(total=len(futures), unit="episode", desc="Downloading") as progress:
            for future in concurrent.futures.as_completed(futures):
                title, mp3_path = future.result()
                mp3_paths[title] = mp3_path
                progress.update(1)
    return mp3_paths


def convert_all_to_wav(mp3_paths: dict, wav_folder: str) -> dict:
    """
    Converts every downloaded mp3 file to wav.

    Args:
        mp3_paths: Dict mapping episode title -> mp3 file path.
        wav_folder: Folder to save wav files in.

    Returns:
        A dict mapping episode title -> wav file path.
    """
    print("\nStep 2/4: Converting mp3 to wav...")
    wav_paths = {}
    for title, mp3_path in tqdm(mp3_paths.items(), unit="episode", desc="Converting"):
        wav_paths[title] = convert_mp3_to_wav(mp3_path, wav_folder)
    return wav_paths


def transcribe_all_to_text(wav_paths: dict, txt_folder: str) -> dict:
    """
    Transcribes every wav file to text.

    Args:
        wav_paths: Dict mapping episode title -> wav file path.
        txt_folder: Folder to save txt files in.

    Returns:
        A dict mapping episode title -> txt file path.
    """
    print("\nStep 3/4: Transcribing audio to text...")
    txt_paths = {}
    for title, wav_path in tqdm(wav_paths.items(), unit="episode", desc="Transcribing"):
        txt_paths[title] = transcribe_wav_to_text(wav_path, txt_folder)
    return txt_paths


def extract_all_quotes(client, txt_paths: dict) -> list[dict]:
    """
    Extract quotes from every transcript using Gemini.

    Args:
        client: An initialized google.genai Client.
        txt_paths: Dict mapping episode title -> txt file path.

    Returns:
        A list of quote dicts, each tagged with its episode title.
    """
    print("\nStep 4/4: Extracting quotes with Gemini...")
    all_quotes = []
    for title, txt_path in tqdm(txt_paths.items(), unit="episode", desc="Extracting quotes"):
        all_quotes.extend(extract_quotes_from_episode(client, txt_path, title))
    return all_quotes


def print_quotes(all_quotes: list[dict]) -> None:
    """
    Print all extracted quotes to the console, each prefixed with the
    episode it came from.

    Args:
        all_quotes: List of dicts with "episode", "author of the quote",
            and "quote" keys.
    """
    if not all_quotes:
        print("No quotes found.")
        return

    print("\n=== Extracted Quotes ===\n")
    for q in all_quotes:
        episode = q.get("episode", "Unknown Episode")
        author = q.get("author of the quote", "Unknown")
        quote = q.get("quote", "")
        print(f"[{episode}] {author}: {quote}")


def main():
    start = time.perf_counter()

    rss_url, podcast_name, num_episodes = get_user_settings()
    api_key = getpass("Gemini API key (hidden while typing, not saved): ").strip()

    # All folders are created automatically, relative to this file's location,
    # so the project runs the same for anyone who clones the repo.
    base_folder = os.path.join(os.getcwd(), Podcast.to_filename(podcast_name))
    mp3_folder = os.path.join(base_folder, MP3_SUBFOLDER)
    wav_folder = os.path.join(base_folder, WAV_SUBFOLDER)
    txt_folder = os.path.join(base_folder, TXT_SUBFOLDER)

    client = genai.Client(api_key=api_key)
    podcast = Podcast(url=rss_url, mp3_folder=mp3_folder)

    print("\nFetching episode list...")
    episodes = podcast.get_episodes(limit=num_episodes)
    print(f"Found {len(episodes)} episode(s).")

    mp3_paths = download_all_episodes(podcast, episodes)
    wav_paths = convert_all_to_wav(mp3_paths, wav_folder)
    txt_paths = transcribe_all_to_text(wav_paths, txt_folder)
    all_quotes = extract_all_quotes(client, txt_paths)

    elapsed = round(time.perf_counter() - start, 2)
    print(f"\nFinished {len(episodes)} episode(s) in {elapsed}s")

    print_quotes(all_quotes)


if __name__ == "__main__":
    main()
