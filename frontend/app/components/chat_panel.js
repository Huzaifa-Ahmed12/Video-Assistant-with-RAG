"use client";

import { useEffect, useRef, useState } from "react";
import { askQuestion } from "../lib/api";

const SUGGESTIONS = ["What were the main points?", "List the action items", "What was decided?"];

export default function ChatPanel() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function ask(question) {
    const q = question.trim();
    if (!q || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const answer = await askQuestion(q);
      setMessages((m) => [...m, { role: "bot", text: answer }]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "bot", text: e.message || "Sorry, I couldn't answer that. Please try again.", error: true },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      ask(input);
    }
  }

  return (
    <div className="card chat">
      <h3 className="chat-title">Chat with this video</h3>

      <div className="messages">
        {messages.length === 0 && (
          <div className="empty">
            <p className="muted">Ask anything about the video. Try one of these:</p>
            <div className="chips">
              {SUGGESTIONS.map((s) => (
                <button key={s} className="chip" onClick={() => ask(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.role} ${m.error ? "error" : ""}`}>
            <p className="prewrap">{m.text}</p>
          </div>
        ))}

        {loading && (
          <div className="bubble bot">
            <span className="dots"><i /><i /><i /></span>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="composer">
        <textarea
          className="input"
          rows={1}
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
        />
        <button className="btn btn-primary" onClick={() => ask(input)} disabled={!input.trim() || loading}>
          Send
        </button>
      </div>
    </div>
  );
}