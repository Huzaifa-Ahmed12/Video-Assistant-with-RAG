import yt_dlp 
from pydub import AudioSegment
import os

DOWNLOAD_DIR='downloads'
os.makedirs(DOWNLOAD_DIR,exist_ok=True) 

#Extract Audio using yt-dlp
def download_youtube_audio(url:str)->str:
    output_path=os.path.join(DOWNLOAD_DIR,"%(title)s.%(ext)s")
    ydl_opts={
        "format":"bestaudio/best",
        "outtmpl":output_path,
        "postprocessors":[
            {
                "key":"FFmpegExtractAudio",
                "preferredcodec":"wav",
                "preferredquality":"192",
            }
        ],
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios"]  # Bypasses 403 Forbidden checks
            }
        },
        "quiet":True,
    }
    #Open the file
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info=ydl.extract_info(url,download=True)
        base_filename = os.path.splitext(ydl.prepare_filename(info))[0]
    return f"{base_filename}.wav"


def convert_to_wav(input_path:str)->str:
    """Convert any audio into wav using pydub"""
    output_path=os.path.splitext(input_path)[0]+"_converted.wav"
    audio=AudioSegment.from_file(input_path)
    audio=audio.set_channels(1).set_frame_rate(16000) # Mono Audio+ Automatically detect file type
    audio.export(output_path,format="wav") 
    return output_path


def chunk_audio(wav_path:str,chunk_minutes:int=10)->list:
    audio=AudioSegment.from_wav(wav_path)
    chunk_ms=chunk_minutes*60*1000
    chunks=[]

    for i,start in enumerate(range(0,len(audio),chunk_ms)):
        chunk=audio[start:start+chunk_ms]
        chunk_path=f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path,format="wav")
        chunks.append(chunk_path)

    return chunks

def process_input(source:str)->list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected Youtube URL. Download Audio....")
        input_path = download_youtube_audio(source) 
    else:
        print("Detected local file....")
        input_path=source

    wav_path=convert_to_wav(input_path)
    print("Chunking Audio...")
    chunks=chunk_audio(wav_path)
    print(f"Audio Ready - len{chunks} created")
    return chunks

