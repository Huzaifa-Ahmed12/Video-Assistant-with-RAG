"use client";

import { useState } from "react";
import { parseActions, parseList } from "../lib/parse";

function Empty({ what }) {
  return (
    <div className="empty-note">
      <strong>No {what} found.</strong>
      <p className="muted">
        This is normal for videos where nobody assigns tasks or makes decisions, such as
        tutorials, lectures and talks. Try a team meeting recording.
      </p>
    </div>
  );
}

export default function Results({ meeting }) {
  const [tab, setTab] = useState("summary");
  const [copied, setCopied] = useState(false);

  const actions = parseActions(meeting.action_items);
  const decisions = parseList(meeting.key_decisions);
  const questions = parseList(meeting.open_questions);

  const tabs = [
    ["summary", "Summary"],
    ["actions", "Action items", actions.length],
    ["decisions", "Decisions", decisions.length],
    ["questions", "Open questions", questions.length],
    ["transcript", "Transcript"],
  ];

  function copyTranscript() {
    navigator.clipboard.writeText(meeting.transcript);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="card results">
      <h2 className="title">{String(meeting.title || "Your video").replace(/\*\*/g, "")}</h2>

      <div className="tabs scroll">
        {tabs.map(([key, label, count]) => (
          <button key={key} className={`tab ${tab === key ? "active" : ""}`} onClick={() => setTab(key)}>
            {label}
            {count !== undefined && <span className="count">{count}</span>}
          </button>
        ))}
      </div>

      <div className="panel">
        {tab === "summary" && (
          <p className="prewrap">{String(meeting.summary).replace(/\*\*/g, "")}</p>
        )}

        {tab === "actions" &&
          (actions.length ? (
            <ul className="cards">
              {actions.map((a, i) => (
                <li key={i} className="item-card">
                  <p className="item-task">{a.task}</p>
                  {(a.owner || a.deadline) && (
                    <div className="meta">
                      {a.owner && <span className="tag"><b>Owner</b> {a.owner}</span>}
                      {a.deadline && <span className="tag"><b>Due</b> {a.deadline}</span>}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <Empty what="action items" />
          ))}

        {tab === "decisions" &&
          (decisions.length ? (
            <ul className="list">
              {decisions.map((d, i) => <li key={i}>{d}</li>)}
            </ul>
          ) : (
            <Empty what="decisions" />
          ))}

        {tab === "questions" &&
          (questions.length ? (
            <ul className="list">
              {questions.map((q, i) => <li key={i}>{q}</li>)}
            </ul>
          ) : (
            <Empty what="open questions" />
          ))}

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