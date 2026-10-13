"use client";

import { useState } from "react";

export default function SourceForm({ onSubmit }) {
  const [mode, setMode] = useState("link"); // link | file
  const [url, setUrl] = useState("");
  const [file, setFile] = useState(null);

  const valid = mode === "link" ? /^https?:\/\/.+\..+/.test(url.trim()) : !!file;

  function submit(e) {
    e.preventDefault();
    if (!valid) return;
    onSubmit(mode === "link" ? { url: url.trim() } : { file });
  }

  return (
    <form className="card" onSubmit={submit}>
      <div className="tabs">
        <button type="button" className={`tab ${mode === "link" ? "active" : ""}`} onClick={() => setMode("link")}>
          Paste a link
        </button>
        <button type="button" className={`tab ${mode === "file" ? "active" : ""}`} onClick={() => setMode("file")}>
          Upload a file
        </button>
      </div>

      {mode === "link" ? (
        <input
          className="input"
          type="url"
          placeholder="https://www.youtube.com/watch?v=..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          autoFocus
        />
      ) : (
        <label className="dropzone">
          <input
            type="file"
            accept="audio/*,video/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            hidden
          />
          {file ? (
            <>
              <strong>{file.name}</strong>
              <span className="muted">{(file.size / 1024 / 1024).toFixed(1)} MB · click to change</span>
            </>
          ) : (
            <>
              <strong>Click to choose an audio or video file</strong>
              <span className="muted">MP4, MP3, WAV, M4A, WEBM and more</span>
            </>
          )}
        </label>
      )}

      <button className="btn btn-primary btn-block" type="submit" disabled={!valid}>
        Generate transcript &amp; notes
      </button>
      <p className="hint">Long videos can take a few minutes. Keep this tab open.</p>
    </form>
  );
}