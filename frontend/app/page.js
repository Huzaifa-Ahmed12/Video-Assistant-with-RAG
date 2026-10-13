"use client";

import { useState } from "react";
import { processSource } from "./lib/api";
import SourceForm from "./components/source_form";
import ProgressView from "./components/progress_view";
import Results from "./components/results";
import ChatPanel from "./components/chat_panel";

export default function Home() {
  const [stage, setStage] = useState("input"); // input | processing | ready
  const [step, setStep] = useState(0);
  const [error, setError] = useState("");
  const [meeting, setMeeting] = useState(null);

  async function handleSubmit(source) {
    setError("");
    setStep(0);
    setStage("processing");
    try {
      const result = await processSource(source, setStep);
      setMeeting(result);
      setStage("ready");
    } catch (e) {
      setError(e.message || "Something went wrong. Please try again.");
      setStage("input");
    }
  }

  function reset() {
    setMeeting(null);
    setError("");
    setStage("input");
  }

  return (
    <main className="page">
      <header className="header">
        <div className="logo">
          <span className="logo-mark">▶</span>
          <span>Video Assistant</span>
        </div>
        {stage === "ready" && (
          <button className="btn btn-ghost" onClick={reset}>
            + New video
          </button>
        )}
      </header>

      {stage === "input" && (
        <section className="hero">
          <h1>Turn any video into notes you can talk to</h1>
          <p className="muted">
            Paste a YouTube link or upload a recording. You'll get a transcript, a summary,
            action items, and a chat that answers questions about it.
          </p>
          {error && <div className="alert">{error}</div>}
          <SourceForm onSubmit={handleSubmit} />
        </section>
      )}

      {stage === "processing" && <ProgressView step={step} />}

      {stage === "ready" && meeting && (
        <section className="workspace">
          <Results meeting={meeting} />
          <ChatPanel />
        </section>
      )}
    </main>
  );
}