"""
transcription.py
Transcribes a 16kHz mono WAV file using local Whisper.
Handles long audio via chunking, language detection, and Urdu translation.
GPU-accelerated when available (CUDA), falls back to CPU automatically.
"""

import whisper
import torch
import json
from pathlib import Path
from pydub import AudioSegment
from pydub.silence import detect_silence

# ---------------------------------------------------------
# 0. Device detection (GPU if available, else CPU)
# ---------------------------------------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
USE_FP16 = DEVICE == "cuda"   # fp16 only works correctly on GPU

print(f"[transcription] Using device: {DEVICE} (fp16={USE_FP16})")


# ---------------------------------------------------------
# 1. Load the model once (reuse across requests)
# ---------------------------------------------------------
_MODEL_CACHE = {}

def load_model(model_size: str = "small"):
    """
    model_size: tiny, base, small, medium, large-v3
    On GPU you can comfortably use medium/large-v3.
    On CPU, stick to small/base for reasonable speed.
    """
    if model_size not in _MODEL_CACHE:
        _MODEL_CACHE[model_size] = whisper.load_model(model_size, device=DEVICE)
    return _MODEL_CACHE[model_size]


# ---------------------------------------------------------
# 2. Detect language from a short sample
# ---------------------------------------------------------
def detect_language(model, wav_path: Path) -> str:
    audio = whisper.load_audio(str(wav_path))
    audio = whisper.pad_or_trim(audio)  # first 30s
    mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)
    _, probs = model.detect_language(mel)
    lang = max(probs, key=probs.get)
    return lang  # e.g. "en", "ur"


# ---------------------------------------------------------
# 3. Split long audio into chunks at silence points
# ---------------------------------------------------------
def chunk_audio(wav_path: Path, chunk_dir: Path,
                 target_len_ms: int = 8 * 60 * 1000,
                 min_silence_len: int = 500,
                 silence_thresh: int = -40) -> list[dict]:
    """
    Returns a list of {"path": Path, "offset_sec": float}
    Splits near silences so words aren't cut mid-speech.
    """
    chunk_dir.mkdir(parents=True, exist_ok=True)
    audio = AudioSegment.from_wav(wav_path)
    total_len = len(audio)

    if total_len <= target_len_ms:
        return [{"path": wav_path, "offset_sec": 0.0}]

    silences = detect_silence(
        audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh
    )
    silence_mid = [ (s + e) // 2 for s, e in silences ]

    chunks = []
    start = 0
    idx = 0
    while start < total_len:
        target_end = start + target_len_ms
        # find nearest silence point to split at, else hard cut
        split_at = min(silence_mid, key=lambda x: abs(x - target_end), default=target_end) \
                   if silence_mid else target_end
        split_at = min(split_at, total_len)
        if split_at <= start:
            split_at = min(target_end, total_len)

        segment = audio[start:split_at]
        out_path = chunk_dir / f"chunk_{idx:03d}.wav"
        segment.export(out_path, format="wav")

        chunks.append({"path": out_path, "offset_sec": start / 1000.0})

        start = split_at
        idx += 1

    return chunks


# ---------------------------------------------------------
# 4. Transcribe a single chunk
# ---------------------------------------------------------
def transcribe_chunk(model, chunk_path: Path, language: str | None,
                      task: str = "transcribe") -> dict:
    """
    task: "transcribe" (keep original language) or "translate" (-> English)
    language: pass detected language to skip re-detection, or None
    """
    result = model.transcribe(
        str(chunk_path),
        language=language,
        task=task,
        fp16=USE_FP16,        # True on GPU, False on CPU
        verbose=False,
        word_timestamps=False,
    )
    return result  # {"text": ..., "segments": [...], "language": ...}


# ---------------------------------------------------------
# 5. Full pipeline: chunk -> transcribe -> merge
# ---------------------------------------------------------
def transcribe_full(wav_path: Path, work_dir: Path,
                     model_size: str = "small") -> dict:

    model = load_model(model_size)

    # Detect language once on the full file
    detected_lang = detect_language(model, wav_path)
    needs_translation = detected_lang == "ur"

    chunk_dir = work_dir / "chunks"
    chunks = chunk_audio(wav_path, chunk_dir)

    all_segments = []
    full_text_parts = []

    for chunk in chunks:
        # Always get the original-language transcript first
        result = transcribe_chunk(
            model, chunk["path"], language=detected_lang, task="transcribe"
        )

        offset = chunk["offset_sec"]
        for seg in result["segments"]:
            all_segments.append({
                "start": round(seg["start"] + offset, 2),
                "end": round(seg["end"] + offset, 2),
                "text": seg["text"].strip(),
            })
        full_text_parts.append(result["text"].strip())

    transcript = {
        "language": detected_lang,
        "device": DEVICE,
        "segments": all_segments,
        "text": " ".join(full_text_parts),
    }

    # Optional: English translation (Whisper's built-in translate task)
    if needs_translation:
        translated_segments = []
        translated_text_parts = []
        for chunk in chunks:
            result = transcribe_chunk(
                model, chunk["path"], language=detected_lang, task="translate"
            )
            offset = chunk["offset_sec"]
            for seg in result["segments"]:
                translated_segments.append({
                    "start": round(seg["start"] + offset, 2),
                    "end": round(seg["end"] + offset, 2),
                    "text": seg["text"].strip(),
                })
            translated_text_parts.append(result["text"].strip())

        transcript["translation"] = {
            "language": "en",
            "segments": translated_segments,
            "text": " ".join(translated_text_parts),
        }

    return transcript


# ---------------------------------------------------------
# 6. Save transcript to disk
# ---------------------------------------------------------
def save_transcript(transcript: dict, out_path: Path):
    out_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------
# Example usage
# ---------------------------------------------------------
if __name__ == "__main__":
    wav_file = Path("meeting.wav")
    work_dir = Path("work")
    work_dir.mkdir(exist_ok=True)

    # On GPU you can bump this to "medium" or "large-v3"
    model_size = "medium" if DEVICE == "cuda" else "small"

    result = transcribe_full(wav_file, work_dir, model_size=model_size)
    save_transcript(result, work_dir / "transcript.json")

    print(f"Detected language: {result['language']}")
    print(f"Segments: {len(result['segments'])}")
    print(result["text"][:500])