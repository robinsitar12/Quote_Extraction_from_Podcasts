import os 
from pydub import AudioSegment

''' 
Transcribe audio files in the mp3 format into wav format for better quality

Attributes:
    CURRENT_DIRECTORY: directory containing downloaded mp3 files of podcast episodes
    DEST_DIRECTORY: destination directory to store transformed wav files of podcast episodes
'''

CURRENT_DIRECTORY = r'C:\Users\robin\OneDrive\Desktop\2_Career\1_Projects\2026_Quote_Extraction_from_Podcasts\Modern_Wisdom\MP3'
DEST_DIRECTORY = r'C:/Users/robin/OneDrive/Desktop/2_Career/1_Projects/2026_Quote_Extraction_from_Podcasts/Modern_Wisdom/WAV'

def transcribe_to_wav(file_path, dest_directory):
    """
    Transcribe audio files in the mp3 format into wav format for better quality
    
    Args:
        file_path: file path to mp3 file in os directory
        dest_directory: destination directory to store the transformed wav files
    """
    
    mp3_file = AudioSegment.from_file(file_path, format="mp3")
    wav_file = mp3_file.set_frame_rate(44100).set_channels(1)
    filename = os.path.splitext(os.path.basename(file_path))[0]
    wav_file.export(f"{dest_directory}/{filename}.wav", format="wav")
 
for name in tqdm(mp3_files, unit = 'episode'):
    transcribe_to_wav(os.path.join(CURRENT_DIRECTORY, name), DEST_DIRECTORY)   
    