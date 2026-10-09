from dotenv import load_dotenv
load_dotenv()

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, get_title
from core.extractor import extract_action_items, extract_key_decision, extract_questions

source="https://www.youtube.com/watch?v=YGgNBcIgI4s"
language="english"

chunks=process_input(source)
transcript=transcribe_all(chunks,language=language)
print("Transcript. \n")
print(transcript)

title=get_title(transcript)
summary=summarize(transcript)

print(f"Title {title}")
print(f"\n Summary {summary}")
print("\n")

action_items=extract_action_items(transcript)
questions=extract_questions(transcript)
decisions=extract_key_decision(transcript)

print(f"Action Items {action_items}\n")
print(f"\n Key Decisions {decisions} \n")
print(f"\n Questions {questions} \n")