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
        "quiet":True,
    }
    #Open the file
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info=ydl.extract_info(url,download=True)
        filename=ydl.prepare_filename(info).replace(".webm",".wav").replace(".m4a",".wav")
    return filename

file=download_youtube_audio("https://www.youtube.com/watch?v=bs1qPy_CWkM")

def convert_to_wav(input_path:str)->str:
    """Convert any audio into wav using pydub"""
    output_path=os.path.splitext(input_path)[0]+"_converted.wav"
    audio=AudioSegment.from_file(input_path)
    audio=audio.set_channels(1).set_frame_rate(16000) # Mono Audio+ Automatically detect file type
    audio.export(output_path,format="wav") 
    return output_path

print(convert_to_wav(file))