"use client";

import { useState } from "react";

function toItems(value) {
  if (Array.isArray(value)) return value;
  if (typeof value === "string") {
    return value
      .split("\n")
      .map((l) => l.replace(/^[\s\-*•\d.]+/, "").trim())
      .filter(Boolean);
  }
  return [];
}

function List({ value, empty }) {
  const items = toItems(value);
  if (!items.length) return <p className="muted">{empty}</p>;
  return (
    <ul className="list">
      {items.map((x, i) => (
        <li key={i}>{x}</li>
      ))}
    </ul>
  );
}

export default function Results({ meeting }) {
  const [tab, setTab] = useState("summary");
  const [copied, setCopied] = useState(false);

  const tabs = [
    ["summary", "Summary"],
    ["actions", "Action items"],
    ["decisions", "Decisions"],
    ["questions", "Open questions"],
    ["transcript", "Transcript"],
  ];

  function copyTranscript() {
    navigator.clipboard.writeText(meeting.transcript);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="card results">
      <h2 className="title">{meeting.title || "Your video"}</h2>

      <div className="tabs scroll">
        {tabs.map(([key, label]) => (
          <button key={key} className={`tab ${tab === key ? "active" : ""}`} onClick={() => setTab(key)}>
            {label}
          </button>
        ))}
      </div>

      <div className="panel">
        {tab === "summary" && <p className="prewrap">{meeting.summary}</p>}
        {tab === "actions" && <List value={meeting.action_items} empty="No action items found." />}
        {tab === "decisions" && <List value={meeting.key_decisions} empty="No decisions found." />}
        {tab === "questions" && <List value={meeting.open_questions} empty="No open questions found." />}
        {tab === "transcript" && (
          <>
            <button className="btn btn-ghost small" onClick={copyTranscript}>
              {copied ? "Copied ✓" : "Copy transcript"}
            </button>
            <p className="prewrap transcript">{meeting.transcript}</p>
          </>
        )}
      </div>
    </div>
  );
}