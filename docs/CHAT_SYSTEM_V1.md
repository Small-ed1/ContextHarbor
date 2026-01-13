# SQLite-Backed Chat Management System v1

## Features Implemented

### 1. Chat Storage (`chatstore.py`)
- SQLite database with WAL mode for performance
- Tables: `chats` and `messages`
- Auto-titling from first user message
- Support for archiving and pinning
- Full CRUD operations

### 2. Chat API Endpoints (`app.py`)
- `GET /api/chats` - List chats (with search & archived filter)
- `POST /api/chats` - Create new chat
- `GET /api/chats/{id}` - Get chat with messages
- `PATCH /api/chats/{id}` - Update title/archived/pinned
- `POST /api/chats/{id}/append` - Add messages to chat
- `POST /api/chats/{id}/clear` - Clear messages, keep chat
- `DELETE /api/chats/{id}` - Delete chat permanently

### 3. Left Sidebar UI (`index.html`)
- Closeable sidebar with overlay
- Two tabs: Chats + Settings
- Hamburger button (☰) to open/close
- Chat list with search and archived toggle
- "New Chat" button
- Chat items with Rename/Archive/Delete actions
- Active chat highlighting

### 4. Sidebar CSS (`styles.css`)
- Fixed positioning (320px wide)
- Smooth slide animation (0.18s)
- Closed state with transform
- Overlay background
- Tab styling with active state
- Chat item styling with preview
- Responsive design

### 5. Chat Management JavaScript (`app.js`)
- `currentChatId` - Track current chat
- `loadChats()` - Fetch and render chat list
- `selectChat(id)` - Load chat messages into state
- `ensureChatSelected()` - Auto-create if no chat selected
- `renderChatList(chats)` - Render chat items with actions
- `appendToChat(role, content, meta)` - Persist messages to DB
- `openSidebar()` / `closeSidebar()` - Sidebar control
- `setTab(which)` - Switch between Chats/Settings panels
- Auto-titling from first user message (DB side)

### 6. Context Support
- Selected chat's full message history loaded
- Messages persist to SQLite on send
- Chat list updates after each message
- Clear button clears messages from DB (not delete chat)
- Context restored on page reload

## Database Schema

### `chats` table
```sql
CREATE TABLE chats (
  id TEXT PRIMARY KEY,           -- UUID
  title TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  archived INTEGER NOT NULL DEFAULT 0,
  pinned INTEGER NOT NULL DEFAULT 0
);
```

### `messages` table
```sql
CREATE TABLE messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chat_id TEXT NOT NULL,
  role TEXT NOT NULL,             -- user/assistant/system
  content TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  model TEXT,                       -- Model used for this message
  meta_json TEXT,                  -- JSON metadata (sources, etc.)
  FOREIGN KEY(chat_id) REFERENCES chats(id) ON DELETE CASCADE
);
```

### Indexes
- `idx_messages_chat_time` - Optimized message queries

## UI Components

### Sidebar Controls
- **Hamburger button** (☰) - Open sidebar
- **Close button** (✕) - Close sidebar
- **Tabs** - Chats / Settings
- **New Chat button** - Create new chat
- **Archived checkbox** - Toggle archived chats
- **Search input** - Filter chats by title
- **Chat list** - Scrollable list of chats

### Chat Item Actions
- **Click** - Select and load chat
- **Rename** - Edit chat title (prompt dialog)
- **Archive/Unarchive** - Toggle archived status
- **Delete** - Delete permanently (with confirmation)

### Settings Panel (moved to sidebar)
- System prompt textarea
- Temperature input
- Context (num_ctx) input
- Keep alive input
- Save/Reset buttons

## Usage Flow

1. **Page Load**
   - Check localStorage for `currentChatId`
   - If none, create "New Chat" and select it
   - Load chat messages into `state.messages`
   - Render chat list

2. **Send Message**
   - Add user message to `state.messages`
   - Append to database via `/api/chats/{id}/append`
   - Create placeholder assistant message
   - Send to Ollama API
   - Stream response
   - Append final response to database
   - Refresh chat list (updates timestamps/previews)

3. **Chat Actions**
   - **Select** - Load chat messages from DB
   - **Rename** - Update title in DB
   - **Archive** - Mark as archived (hide from default list)
   - **Delete** - Remove chat and all messages
   - **Clear** - Remove messages, keep chat entry

4. **Settings**
   - Settings panel moved from right drawer to sidebar
   - Saves persist to localStorage
   - Applied to subsequent chat requests

## Technical Details

### Auto-Titling
When first user message is sent to a "New Chat":
- Extract first 7 words
- Truncate to 60 chars
- Update chat title in DB
- Fallback to "New Chat" if no user message

### Message Persistence
- User message appended immediately on send
- Assistant message appended after stream completes
- Meta JSON includes RAG sources if applicable
- Updated timestamps for sorting

### Chat List Rendering
- Sorted by `pinned DESC, updated_at DESC`
- Shows preview of last message (first 180 chars)
- Active chat highlighted with outline
- Archived chats only shown when checkbox checked
- Search filters by title prefix

### State Management
- `state.messages` - In-memory message buffer
- `state.settings` - Settings (system, temperature, num_ctx, keep_alive)
- `state.model` - Selected model
- `localStorage` - Persists currentChatId and app state

## Database Initialization
```python
# On app startup
chatstore.init_db()
```

Creates tables if they don't exist, adds indexes.

## Current Status

✅ SQLite database (`chat.sqlite3`) created
✅ Chat storage with full CRUD
✅ API endpoints working
✅ Sidebar UI with closeable design
✅ Tabs: Chats + Settings
✅ Search + Archived filter
✅ Auto-titling from first message
✅ Context support (history restored on select)
✅ Message persistence on send
✅ Chat list updates in real-time
✅ Clear chat (delete messages, keep chat)
✅ Rename/Archive/Delete actions
✅ Both servers running (FastAPI port 8000, Ollama port 11434)

## Files Modified

- `chatstore.py` - NEW - Chat storage and database operations
- `app.py` - Added chat API endpoints
- `static/index.html` - Added sidebar, removed old drawer
- `static/styles.css` - Added sidebar styling
- `static/app.js` - Added chat management logic

## Testing

```bash
# Create chat
curl -X POST http://localhost:8000/api/chats \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Chat"}'

# List chats
curl http://localhost:8000/api/chats

# Get chat with messages
curl http://localhost:8000/api/chats/{chat_id}

# Append message
curl -X POST http://localhost:8000/api/chats/{chat_id}/append \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'

# Clear chat
curl -X POST http://localhost:8000/api/chats/{chat_id}/clear

# Delete chat
curl -X DELETE http://localhost:8000/api/chats/{chat_id}
```

## Next Options

Pick ONE for v2:

1. **Per-chat settings** - Save model/temperature/system prompt per chat
2. **Export / Import** - Download chat as JSON, upload to restore
3. **Pin + folders/tags** - Organize chats with tags and pinning
4. **Autosummarize old messages** - Summarize context, keep history small
