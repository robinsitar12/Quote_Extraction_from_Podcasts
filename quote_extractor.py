"""
Uses Google Gemini (if not specified differently in config.py) to extract quotes and their authors from podcast transcripts.
"""

import json
import time
from config import GEMINI_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, GEMINI_REQUEST_DELAY_SECONDS


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """
    Split text into overlapping chunks of `size` words each, so long
    transcripts fit within the model's context window and quotes that fall
    near a chunk boundary aren't cut off and lost.

    Args:
        text: Full transcript text.
        size: Number of words per chunk.
        overlap: Number of words shared between consecutive chunks.

    Yields:
        Chunks of the transcript as strings.
    """
    words = text.split()
    for i in range(0, len(words), size - overlap):
        yield " ".join(words[i:i + size])

def extract_quotes_from_chunk(client, chunk: str) -> list[dict]:
    """
    Ask Gemini to extract quotes and their authors from one transcript chunk.

    Args:
        client: An initialized google.genai Client.
        chunk: A piece of transcript text.

    Returns:
        A list of dicts like {"author of the quote": "...", "quote": "..."}.
    """

    prompt = f"""You are analyzing a podcast transcript.

The transcript is a transcription of people speaking in a podcast.

YOUR TASK IS NOT to extract things the podcast speakers themselves say.

Instead, extract ONLY quotations that are quoted INSIDE the conversation.

Examples:
- A speaker says: Thomas once said, "Success is never owned, it is rented." → Extract this.
- A speaker says: My grandfather always told me: "Treat people with kindness." → Extract this.
- A speaker says: Einstein wrote, "Imagination is more important than knowledge." → Extract this.

DO NOT extract the ordinary dialogue of the podcast speakers.

This is the single most important rule.

If Wendy says:
"The tools available now are amazing."

this is NOT a quote.
It is simply Wendy speaking in the podcast.

If the host says:
"I think language learning should be fun."

this is NOT a quote.

If someone says:
"My teacher always told me: 'Practice every day.'"

then ONLY extract:

"My teacher always told me: 'Practice every day.'"

because it is a quotation embedded inside the conversation.

STRICT RULES

1. Only extract quotations that are embedded within the podcast conversation.

2. Never extract the podcast speakers' own dialogue, opinions, explanations or advice, even if they are complete sentences.

3. A valid quote must be explicitly attributed as something another person previously said, wrote or is being quoted as saying.

4. Ignore every sentence that is simply part of the ongoing conversation between the podcast participants.

5. The quoted person must be clearly identifiable.
If the source is vague ("someone said", "people say", "a friend once said"), skip it.

6. Only return quotes that are explicitly presented as quotations.
Do NOT infer quotations from paraphrases.

7. If no embedded quotations exist, return [].

Return ONLY valid JSON:

[
  {{
    "author of the quote": "...",
    "quote": "..."
  }}
]

Text:
{chunk}"""

    resp = client.models.generate_content(model="gemini-3.1-flash-lite", contents=prompt)
    try:
        return json.loads(resp.text.strip("```json").strip("```"))
    except json.JSONDecodeError:
        return []


def extract_quotes_from_episode(client, txt_path: str, episode_title: str) -> list[dict]:
    """
    Extract all quotes from one episode's transcript file, tagging each
    quote with the episode title it came from.

    Args:
        client: An initialized google.genai Client.
        txt_path: Path to the episode's transcript .txt file.
        episode_title: Name of the podcast episode, attached to every quote.

    Returns:
        A list of dicts like:
        {"episode": ..., "author of the quote": ..., "quote": ...}
    """
    with open(txt_path, encoding="utf-8") as f:
        transcript = f.read()

    episode_quotes = []
    for chunk in chunk_text(transcript):
        for quote in extract_quotes_from_chunk(client, chunk):
            quote["episode"] = episode_title
            episode_quotes.append(quote)
        time.sleep(GEMINI_REQUEST_DELAY_SECONDS)  # stay under the free-tier rate limit

    return episode_quotes