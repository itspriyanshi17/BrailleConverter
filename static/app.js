const $ = (id) => document.getElementById(id);

const textBox = $("text");
const status = $("ocr-status");
let last = null; // last /api/convert result

// ── Tabs ──────────────────────────────────────────────
for (const tab of document.querySelectorAll('[role="tab"]')) {
  tab.addEventListener("click", () => {
    for (const t of document.querySelectorAll('[role="tab"]')) {
      const selected = t === tab;
      t.setAttribute("aria-selected", selected);
      $(t.getAttribute("aria-controls")).hidden = !selected;
    }
    if (tab.id === "tab-type") textBox.focus();
  });
}

// ── Photo → text ──────────────────────────────────────
function setStatus(message, kind = "") {
  status.textContent = message;
  status.className = "status " + kind;
}

async function readPhoto(file) {
  if (!file) return;
  $("preview-img").src = URL.createObjectURL(file);
  $("preview").hidden = false;
  setStatus("Reading text from the photo… (the first time for a language takes longer)", "busy");

  const form = new FormData();
  form.append("image", file);
  form.append("lang", $("lang").value);
  try {
    const res = await fetch("/api/ocr", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Something went wrong.");
    if (!data.text.trim()) {
      setStatus("No text found. Try a closer, brighter photo with the page flat.", "error");
      return;
    }
    textBox.value = data.text;
    const how = $("lang").value === "auto" ? ` Detected: ${data.language}.` : "";
    if (data.low_confidence) {
      setStatus(`This photo was hard to read, so expect mistakes.${how} For better results, use a sharper, closer photo in good light, with printed (not handwritten) text.`, "error");
    } else {
      setStatus(`Done.${how} Check the text below and fix any mistakes.`);
    }
    convert();
  } catch (err) {
    setStatus(err.message === "Failed to fetch" ? "Could not reach the server. Is app.py still running?" : err.message, "error");
  }
}

for (const id of ["camera", "upload"]) {
  $(id).addEventListener("change", (e) => {
    readPhoto(e.target.files[0]);
    e.target.value = ""; // allow choosing the same file again
  });
}

// ── Text → Braille ────────────────────────────────────
let timer;
textBox.addEventListener("input", () => {
  clearTimeout(timer);
  timer = setTimeout(convert, 250);
});

async function convert() {
  const text = textBox.value;
  $("text-meta").textContent = text ? `${[...text].length} characters` : "";
  if (!text.trim()) {
    $("output").hidden = true;
    last = null;
    return;
  }
  const res = await fetch("/api/convert", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  const data = await res.json();
  if (!res.ok) {
    $("text-meta").textContent = data.error;
    return;
  }
  if (text !== textBox.value) return; // a newer edit is on its way
  last = { ...data, text };
  render(data);
}

function render(data) {
  $("output").hidden = false;
  $("braille").textContent = data.braille;

  const unknown = $("unknown");
  unknown.hidden = !data.unknown.length;
  unknown.textContent = data.unknown.length
    ? `No Braille for: ${data.unknown.join(" ")} — shown as ⠿`
    : "";

  // Lines hold words, words hold letters, so a word never breaks across rows.
  const cells = $("cells");
  cells.replaceChildren();
  let line = newLine();
  let word = newWord();
  const endWord = () => {
    if (word.childElementCount) line.append(word);
    word = newWord();
  };
  for (const [src, braille] of data.units) {
    if (braille === "\n") {
      endWord();
      cells.append(line);
      line = newLine();
    } else if (!src.trim()) {
      endWord();
    } else {
      word.append(unitEl(src, braille));
    }
  }
  endWord();
  cells.append(line);
}

function newWord() {
  const el = document.createElement("div");
  el.className = "cell-word";
  return el;
}

function newLine() {
  const el = document.createElement("div");
  el.className = "cell-line";
  return el;
}

// Dots 1-3 are the left column, 4-6 the right; grid fills row by row.
const ORDER = [1, 4, 2, 5, 3, 6];

function unitEl(src, braille) {
  const unit = document.createElement("div");
  const cellChars = [...braille];
  unit.className = "unit" + (cellChars.length > 1 ? " multi" : "");

  const row = document.createElement("div");
  row.className = "unit-cells";
  const spoken = [];
  for (const ch of cellChars) {
    const mask = ch.codePointAt(0) - 0x2800;
    const cell = document.createElement("div");
    cell.className = "cell";
    const raised = [];
    for (const d of ORDER) {
      const dot = document.createElement("span");
      const on = mask & (1 << (d - 1));
      dot.className = "dot" + (on ? " on" : "");
      cell.append(dot);
    }
    for (let d = 1; d <= 6; d++) if (mask & (1 << (d - 1))) raised.push(d);
    spoken.push(raised.length ? "dots " + raised.join(" ") : "blank");
    row.append(cell);
  }
  const label = document.createElement("div");
  label.className = "unit-label";
  label.textContent = src;

  unit.setAttribute("role", "img");
  unit.setAttribute("aria-label", `${src}: ${spoken.join(", then ")}`);
  unit.append(row, label);
  return unit;
}

// ── Copy & downloads ──────────────────────────────────
function download(blob, name) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

$("copy").addEventListener("click", async (e) => {
  if (!last) return;
  let ok = false;
  try {
    await navigator.clipboard.writeText(last.braille); // needs https or localhost
    ok = true;
  } catch {
    // Phone over plain http: fall back to selecting hidden text and copying it.
    const tmp = document.createElement("textarea");
    tmp.value = last.braille;
    document.body.append(tmp);
    tmp.select();
    ok = document.execCommand("copy");
    tmp.remove();
  }
  e.target.textContent = ok ? "Copied ✓" : "Copy failed";
  setTimeout(() => (e.target.textContent = "Copy"), 1500);
});

$("dl-txt").addEventListener("click", () => {
  if (last) download(new Blob([last.braille + "\n"], { type: "text/plain;charset=utf-8" }), "braille.txt");
});

$("dl-brf").addEventListener("click", () => {
  if (last) download(new Blob([last.brf], { type: "text/plain" }), "braille.brf");
});

$("dl-png").addEventListener("click", async (e) => {
  if (!last) return;
  e.target.disabled = true;
  try {
    const res = await fetch("/api/png", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: last.text }),
    });
    if (res.ok) download(await res.blob(), "braille.png");
  } finally {
    e.target.disabled = false;
  }
});

// A link like /?text=Hello opens with that text already converted.
const shared = new URLSearchParams(location.search).get("text");
if (shared) {
  textBox.value = shared;
  convert();
}
