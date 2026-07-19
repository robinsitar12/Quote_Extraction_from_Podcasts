import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence
from tqdm import tqdm
from faster_whisper import WhisperModel

''' 
Transcribe mp3 files into .wav format, then transcribe speech into .txt files

Attributes:
    CURRENT_DIRECTORY: directory containing downloaded .mp3 files of podcast episodes
    WAV_DIRECTORY: destination directory to store transformed .wav files of podcast episodes
    TXT_DIRECTORY: destination directory to store transcribed .txt files
'''

CURRENT_DIRECTORY = r'C:/Users/robin/OneDrive/Desktop/2_Career/1_Projects/2026_Quote_Extraction_from_Podcasts/Modern_Wisdom'
WAV_DIRECTORY = r'C:/Users/robin/OneDrive/Desktop/2_Career/1_Projects/2026_Quote_Extraction_from_Podcasts/Modern_Wisdom/WAV'
TXT_DIRECTORY = r'C:/Users/robin/OneDrive/Desktop/2_Career/1_Projects/2026_Quote_Extraction_from_Podcasts/Modern_Wisdom/TXT'


def transcribe_to_wav(file_path, wav_directory):
    """
    Transcribe audio files in the .mp3 format into wav format for better quality
    
    Args:
        file_path: file path to .mp3 file in os directory
        wav_directory: directory to store the transformed .wav files
    """
    
    mp3_file = AudioSegment.from_file(file_path, format="mp3")
    wav_file = mp3_file.set_frame_rate(44100).set_channels(1)
    filename = os.path.splitext(os.path.basename(file_path))[0]
    wav_file.export(f"{wav_directory}/{filename}.wav", format="wav")

model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_wav_to_text(wav_path, txt_directory):
    '''
    Transcribe speech in a wav file into text and save it as a .txt file
    
    Args:
        wav_path: path to the .wav file to transcribe
        txt_directory: directory to store the transformed .txt files
    '''
    
    segments, info = model.transcribe(wav_path)
    
    full_text = " ".join(segment.text.strip() for segment in segments)
    
    filename = os.path.splitext(os.path.basename(wav_path))[0]
    txt_path = os.path.join(txt_directory, f"{filename}.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(full_text)  
    
mp3_files = [name for name in os.listdir(CURRENT_DIRECTORY) if name.lower().endswith('.mp3')]

os.makedirs(WAV_DIRECTORY, exist_ok=True)
os.makedirs(TXT_DIRECTORY, exist_ok=True)   

for name in tqdm(mp3_files, unit = 'epsiode'):
    mp3_path = os.path.join(CURRENT_DIRECTORY, name)
    transcribe_to_wav(mp3_path, WAV_DIRECTORY)
    
    filename = os.path.splitext(name)[0]
    wav_path = os.path.join(WAV_DIRECTORY, f"{filename}.wav")
    transcribe_wav_to_text(wav_path, TXT_DIRECTORY)