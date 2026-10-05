import whisper
import os

WHISPER_MODEL=os.getenv("WHISPER_MODEL","small")

_model=None

# Load Model locally
def load_model():
    global _model
    if _model is None:
        print(f"Loading Model......")
        _model=whisper.load_model(WHISPER_MODEL)
        print(f"Whisper Model Loaded")

    return _model


# Transcribe Single Chunk
def transcribe_chunk(chunk_path:str,translate:bool=False)->str:
    model=load_model()
    task="translate" if translate else "transcribe"
    result=model.transcribe(
    chunk_path,
    task=task,
    temperature=0.0,
)

    return result['text']

# Transcribe All Chunks
def transcribe_all(chunks:list,translate:bool=False)->str:
    full_transcript=" "

    for i,chunk in enumerate(chunks):
        print(f"Transcribing Chunk {i+1}")
        text=transcribe_chunk(chunk,translate=translate)
        full_transcript+=text + " "
    print("Transcriptions Completed....")

    return full_transcript