"""
Shared configuration and constants for the podcast quote extraction pipeline.
"""

# Maximum number of episodes a user is allowed to request per run
MAX_EPISODES = 5

# Whisper model size used for speech-to-text (see faster-whisper docs for
# available options: tiny, base, small, medium, large-v3, etc.)
WHISPER_MODEL_SIZE = "base"

# Gemini model used for quote extraction
GEMINI_MODEL = "gemini-3.1-flash-lite"

# Text chunking settings for the Gemini prompt (in words)
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200

# Delay between Gemini requests, to stay under the free-tier rate limit (~15 requests/min)
GEMINI_REQUEST_DELAY_SECONDS = 4.5

# Subfolder names created inside the podcast's main folder
MP3_SUBFOLDER = "MP3"
WAV_SUBFOLDER = "WAV"
TXT_SUBFOLDER = "TXT"