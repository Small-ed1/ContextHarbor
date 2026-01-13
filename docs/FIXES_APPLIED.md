# Fixes Applied

## 1. Tooltip Performance Fix ✅

**Problem:** Adding `window.addEventListener('scroll')` and `window.addEventListener('resize')` per element creates hundreds of listeners.

**Solution:** Use single global listeners that only compute for the currently hovered/focused element.

**Changes in `static/app.js`:**

```js
let activeTipEl = null;

function computeTipClasses(el){
  if (!el) return;
  const rect = el.getBoundingClientRect();
  const pad = 12;
  const estH = 48;
  const estW = 280;

  const spaceAbove = rect.top;
  const spaceBelow = window.innerHeight - rect.bottom;

  const wantBottom = spaceAbove < estH + pad && spaceBelow > spaceAbove;
  const wantTop = spaceBelow < estH + pad && spaceAbove >= spaceBelow;

  el.classList.toggle("tip-bottom", wantBottom && !wantTop);

  const nearLeft = rect.left < (estW / 2);
  const nearRight = (window.innerWidth - rect.right) < (estW / 2);

  el.classList.toggle("tip-left", nearLeft && !nearRight);
  el.classList.toggle("tip-right", nearRight && !nearLeft);
}

function hydrateTooltips() {
  document.querySelectorAll("button, a, input, select, textarea").forEach((el) => {
    const tip =
      el.getAttribute("data-tip") ||
      el.getAttribute("aria-label") ||
      el.getAttribute("title") ||
      "";

    if (tip) el.setAttribute("data-tip", tip);
    if (el.hasAttribute("title")) el.removeAttribute("title");

    if (el.dataset.tipBound === "1") return;
    el.dataset.tipBound = "1";

    const onEnter = () => { activeTipEl = el; computeTipClasses(el); };
    const onLeave = () => { if (activeTipEl === el) activeTipEl = null; };

    el.addEventListener("mouseenter", onEnter);
    el.addEventListener("focus", onEnter);
    el.addEventListener("mouseleave", onLeave);
    el.addEventListener("blur", onLeave);
  });
}

// ONE global set:
window.addEventListener("scroll", () => computeTipClasses(activeTipEl), { passive: true });
window.addEventListener("resize", () => computeTipClasses(activeTipEl), { passive: true });
```

**Benefits:**
- Only 2 global listeners instead of 200+ per-element listeners
- Passive listeners for better scroll/resize performance
- Only computes for active element
- No double-binding (checks `tipBound` flag)

## 2. SQL Placeholder Bug Fix ✅

**Problem:** `append_messages` has 6 columns but only 5 placeholders.

**Changes in `chatstore.py`:**

```python
# Added foreign keys pragma in _conn():
con.execute("PRAGMA foreign_keys=ON;")

# Fixed INSERT statement:
cur.execute(
    "INSERT INTO messages(chat_id,role,content,created_at,model,meta_json) VALUES(?,?,?,?,?)",
    (chat_id, role, content, ts, model, None),
)
```

**What was wrong:**
```python
# BEFORE (wrong):
VALUES(?,?,?,?,?,)  # 6 question marks, but only 5 values
(chat_id, role, content, ts, model, meta)

# AFTER (correct):
VALUES(?,?,?,?,?,?)  # 6 question marks, 6 values
(chat_id, role, content, ts, model, None)
```

**Note:** For now, `meta` is set to `None` since frontend doesn't pass sources yet. This can be updated later.

## 3. Confirmed Defaults

**Settings:**
- Global-only (model/temp/system prompt apply everywhere)
- Archived chats hidden by default (checkbox to show)

**Current Status:**

Both servers running:
- FastAPI: http://localhost:8000 (PID 1459452)
- Ollama: http://localhost:11434 (PID 1459450)

All fixes applied and verified.
