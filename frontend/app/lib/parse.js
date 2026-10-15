const EMPTY_VALUE = /^(none|n\/a|not specified|unspecified|unknown|-)\.?$/i;

function isNone(text) {
  const t = text.trim();
  return (
    !t ||
    /^(none|n\/a|nothing)\b[^\n]{0,60}$/i.test(t) ||
    /^no\b[^\n]{0,100}\b(found|identified|mentioned|discussed|detected)\b/i.test(t)
  );
}

// Returns an array of blocks; each block is an array of lines for one item.
function toBlocks(value) {
  if (Array.isArray(value)) {
    return value
      .map((v) => [String(v).replace(/\*\*/g, "").trim()])
      .filter((b) => b[0]);
  }
  if (typeof value !== "string") return [];

  const clean = value.replace(/\*\*/g, "");
  if (isNone(clean)) return [];

  const blocks = [];
  let current = null;
  for (const line of clean.split("\n")) {
    const m = line.match(/^ ?(?:\d+[.)]|[-*•])\s+(.*)$/);
    if (m) {
      current = [m[1].trim()];
      blocks.push(current);
    } else if (current && line.trim()) {
      current.push(line.trim());
    }
    // lines before the first numbered item (an intro sentence) are ignored
  }
  if (blocks.length) return blocks;

  return clean
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean)
    .map((l) => [l]);
}

export function parseList(value) {
  return toBlocks(value)
    .map((lines) => lines.join(" ").trim())
    .filter(Boolean);
}

function field(text, label) {
  const m = text.match(new RegExp(`${label}\\s*:\\s*(.+)`, "i"));
  const v = m ? m[1].trim() : "";
  return EMPTY_VALUE.test(v) ? "" : v;
}

export function parseActions(value) {
  return toBlocks(value)
    .map((lines) => {
      const text = lines.join("\n");
      const task = field(text, "task description") || field(text, "task") || lines[0];
      return {
        task,
        owner: field(text, "owner"),
        deadline: field(text, "deadline"),
      };
    })
    .filter((a) => a.task);
}