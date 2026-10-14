// MOCK DATA LAYER. Replace the bodies of these two functions with real
// fetch() calls when your backend is ready. The UI will not need changes.
// This is just the dummy data And it will change after connection with backend 
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

export const STEPS = [
  "Downloading and preparing audio",
  "Transcribing speech",
  "Writing the summary",
  "Finding action items and decisions",
  "Setting up chat",
];

// source = { url } or { file }
// onStep(index) is called as each pipeline stage starts
export async function processSource(source, onStep) {
  for (let i = 0; i < STEPS.length; i++) {
    onStep(i);
    await wait(1400);
  }

  return {
    title: source.file ? source.file.name : "Weekly Product Planning Meeting",
    summary:
    "Currently No summary Because no backend is connected.",
    action_items: [
      "No Backend, so no action items."
    ],
    key_decisions: [
        "Also No key decisions for now."
    ],
    open_questions: [
      "Currenlty No Open Questions."
    ],
    transcript:
    "No Transcript for now."
  };
}

export async function askQuestion(question) {
  await wait(1200);
  return `This is a sample answer to: "${question}"\n\nWhen the backend is connected, the answer will come from your RAG chain and be based on the actual transcript.`;
}