from dotenv import load_dotenv

load_dotenv()

from core.extractor import extract_action_items, extract_key_decision, extract_questions

TRANSCRIPT = """
Sara: Welcome everyone to the weekly planning meeting. Let's start with the release status.
Ali: Testing is almost done, but we found issues with large video uploads.
Sara: In that case we decided to move the launch date by one week.
Hamza: Agreed. I will draft the launch announcement by Thursday.
Ali: I'll fix the upload size limit and report back at the next meeting.
Sara: Great. Sara will also finalize the onboarding screens by Friday.
Hamza: One question: do we support files larger than 2 GB at launch?
Sara: Good point, we haven't answered that yet. Also, who approves the final announcement text?
Ali: We decided that testing will focus on large uploads first.
"""

tests = [
    ("ACTION ITEMS", extract_action_items),
    ("KEY DECISIONS", extract_key_decision),
    ("OPEN QUESTIONS", extract_questions),
]

for name, fn in tests:
    print("=" * 50)
    print(name)
    try:
        result = fn(TRANSCRIPT)
        print("TYPE:", type(result))
        print("REPR:", repr(result))
        print("PRETTY:\n", result)
    except Exception as e:
        print("ERROR:", type(e).__name__, "-", e)