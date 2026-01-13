# Fixes Applied - Final

## 1. Tooltip Performance Fix ✅

**Problem:** Adding `window.addEventListener('scroll')` and `window.addEventListener('resize')` per element created hundreds of global listeners, causing severe performance issues.

**Solution:** Use single global listeners that only compute position for the currently hovered/focused element.

### Changes in `static/app.js`

**Added:**
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
- Only **2 global listeners** instead of 200+ per-element listeners
- Passive listeners for better scroll/resize performance
- Only computes position for active element
- No double-binding (checks `tipBound` flag)
- Clean event lifecycle

## 2. SQL Placeholder Bug Fix ✅

**Problem:** `append_messages` function had 6 columns but only 5 placeholders in SQL, causing `sqlite3.OperationalError: 5 values for 6 columns`.

### Changes in `chatstore.py`

**Fixed SQL statement:**
```python
# BEFORE (wrong):
cur.execute(
    "INSERT INTO messages(chat_id,role,content,created_at,model,meta_json) VALUES(?,?,?,?,?)",
    (chat_id, role, content, ts, model, None),  # 6 values, but only 5 ? placeholders
)

# AFTER (correct):
cur.execute(
    "INSERT INTO messages(chat_id,role,content,created_at,model,meta_json) VALUES(?,?,?,?,?,?)",
    (chat_id, role, content, ts, model, None),  # 6 values, 6 ? placeholders
)
```

**Also added foreign keys support:**
```python
def _conn():
    con = sqlite3.connect(CHAT_DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    con.execute("PRAGMA foreign_keys=ON;")  # Added this
    return con
```

## 3. Confirmed Defaults ✅

**Settings:**
- Global-only settings (model/temp/system prompt apply everywhere)
- Archived chats are hidden by default (checkbox to show them)

## Current Status

Both servers running:
- FastAPI: http://localhost:8000 (PID 1478616)
- Ollama: http://localhost:11434 (PID 1478614)

All fixes applied and verified working:
- ✅ 2 global tooltip listeners (was 200+)
- ✅ SQL INSERT has correct 6 placeholders for 6 columns
- ✅ Foreign keys enabled
- ✅ Tooltip edge-aware positioning (top/bottom/left/right)
- ✅ Text wrapping for long tooltips
- ✅ No double-binding events
