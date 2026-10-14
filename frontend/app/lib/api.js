const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

export const STEPS = [
  "Downloading and preparing audio",
  "Transcribing speech",
  "Writing the summary",
  "Finding action items and decisions",
  "Setting up chat",
];

async function request(path, options) {
  let res;
  try {
    res = await fetch(`${API}${path}`, options);
  } catch {
    throw new Error("Can't reach the server. Make sure the backend is running.");
  }

  if (!res.ok) {
    let detail = "Something went wrong. Please try again.";
    try {
      const data = await res.json();
      if (typeof data.detail === "string") detail = data.detail;
    } catch {}
    throw new Error(detail);
  }
  return res.json();
}

// source = { url } or { file }
// onStep(index) is called when the backend moves to a new stage
export async function processSource(source, onStep) {
  const form = new FormData();
  if (source.file) form.append("file", source.file);
  else form.append("url", source.url);

  const { job_id } = await request("/api/jobs", { method: "POST", body: form });

  while (true) {
    await wait(2000);
    const job = await request(`/api/jobs/${job_id}`);
    onStep(job.step ?? 0);

    if (job.status === "done") {
      return request(`/api/meetings/${job.meeting_id}`);
    }
    if (job.status === "error") {
      throw new Error(job.error || "Processing failed. Please try again.");
    }
  }
}

export async function askQuestion(meetingId, question) {
  const data = await request("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ meeting_id: meetingId, question }),
  });
  return data.answer;
}