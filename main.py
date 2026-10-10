from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, get_title
from core.extractor import extract_action_items, extract_key_decision, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

def run_pipeline(source: str):
    print("Starting AI Video Assistant")
    chunks = process_input(source)
    transcript = transcribe_all(chunks)
    print(f"Raw Transcription: \n {transcript}")
    title = get_title(transcript)
    summary = summarize(transcript)
    action_items = extract_action_items(transcript)
    key_decisions = extract_key_decision(transcript)
    questions = extract_questions(transcript)

    rag_chain = build_rag_chain(transcript)
    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": key_decisions,
        "open_questions": questions,
        "rag_chain": rag_chain
    }

if __name__ == "__main__":
    video = "https://www.youtube.com/watch?v=12JK4Q_6Pyo"
    source = video.strip()
    result = run_pipeline(source)

    print("-" * 10)
    print(f"Title: {result['title']}")
    print(f"\n Summary: {result['summary']}")
    print(f"\n Action Items: {result['action_items']}")
    print(f"\n Key Decisions: {result['key_decisions']}")
    print(f"\n Open Questions: {result['open_questions']}")

    print("-" * 10)
    print("\n Chat with the Meeting. Type exit to quit. \n")
    rag_chain = result['rag_chain']
    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit", "q"]:
            print("Good Bye")
            break
        if not question:
            continue
        answer = ask_question(rag_chain, question)
        print(f"RAG Assistant: {answer}\n")
