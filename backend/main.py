from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, get_title
from core.extractor import extract_action_items, extract_key_decision, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

def run_pipeline(source: str, on_step=None):
    def step(i):
        if on_step:
            on_step(i)

    print("Starting AI Video Assistant")
    step(0)  # downloading and preparing audio
    chunks = process_input(source)

    step(1)  # transcribing
    transcript = transcribe_all(chunks)
    print(f"Raw Transcription: \n {transcript}")

    step(2)  # title and summary
    title = get_title(transcript)
    summary = summarize(transcript)

    step(3)  # action items, decisions, questions
    action_items = extract_action_items(transcript)
    key_decisions = extract_key_decision(transcript)
    questions = extract_questions(transcript)

    step(4)  # chat setup
    rag_chain = build_rag_chain(transcript)

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": key_decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }

if __name__ == "__main__":
    video = "https://www.youtube.com/watch?v=YGgNBcIgI4s"
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
