import { STEPS } from "../lib/api";

export default function ProgressView({ step }) {
  return (
    <section className="hero center">
      <div className="spinner" />
      <h2>Working on your video</h2>
      <p className="muted">Step {Math.min(step + 1, STEPS.length)} of {STEPS.length}</p>

      <ol className="steps">
        {STEPS.map((label, i) => {
          const state = i < step ? "done" : i === step ? "active" : "todo";
          return (
            <li key={label} className={`step ${state}`}>
              <span className="step-dot">{state === "done" ? "✓" : i + 1}</span>
              {label}
            </li>
          );
        })}
      </ol>

      <p className="hint">This can take a few minutes for long videos.</p>
    </section>
  );
}