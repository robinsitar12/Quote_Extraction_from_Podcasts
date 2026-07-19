import time
import concurrent.futures
from tqdm import tqdm

from podcast import Podcast

if __name__ == "__main__":
    start = time.perf_counter()

    podcast = Podcast(url=Podcast.PODCAST_URL, name=Podcast.PODCAST_NAME)
    podcast.setup_folder()

    print("Fetching episode list...")
    episodes = podcast.get_episodes()
    print(f"Found {len(episodes)} episodes. Starting download...\n")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(podcast.download_episodes, ep): ep for ep in episodes}
        with tqdm(total=len(futures), unit="episode") as progress:
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                progress.set_postfix_str(result)
                progress.update(1)

    elapsed = round(time.perf_counter() - start, 2)
    print(f"\nFinished {len(episodes)} episodes in {elapsed}s")