-- SQLite schema for Router Phase 1
-- Run with: sqlite3 router.db < schema.sql

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- Users and sessions
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  config TEXT,  -- JSON global settings
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  token TEXT UNIQUE,
  started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  permissions TEXT,  -- JSON per-session overrides
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Chats and messages (enhanced)
CREATE TABLE chats (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  session_id INTEGER,
  title TEXT NOT NULL DEFAULT 'New Chat',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  archived BOOLEAN DEFAULT FALSE,
  summary TEXT,
  context_vector BLOB,  -- For RAG similarity (compressed)
  FOREIGN KEY(user_id) REFERENCES users(id),
  FOREIGN KEY(session_id) REFERENCES sessions(id)
);

CREATE TABLE messages (
  id INTEGER PRIMARY KEY,
  chat_id INTEGER NOT NULL,
  role TEXT NOT NULL,  -- user/assistant/system
  content TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  tokens INTEGER DEFAULT 0,
  embedding BLOB,  -- Message embeddings for RAG
  FOREIGN KEY(chat_id) REFERENCES chats(id) ON DELETE CASCADE
);

-- Research sessions
CREATE TABLE research_sessions (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  topic TEXT NOT NULL,
  status TEXT DEFAULT 'pending',  -- pending/running/completed/failed
  allocated_time_hours REAL,
  time_remaining REAL,
  started_at DATETIME,
  completed_at DATETIME,
  config TEXT,  -- JSON research config
  results TEXT,  -- JSON results
  FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Tools and permissions
CREATE TABLE tools (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  category TEXT DEFAULT 'general',  -- system/web/ai/knowledge
  default_permission TEXT DEFAULT 'ask'  -- allow/ask/deny
);

CREATE TABLE tool_permissions (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  tool_id INTEGER NOT NULL,
  permission TEXT NOT NULL,
  session_id INTEGER,  -- NULL for global
  FOREIGN KEY(user_id) REFERENCES users(id),
  FOREIGN KEY(tool_id) REFERENCES tools(id),
  FOREIGN KEY(session_id) REFERENCES sessions(id)
);

-- RAG knowledge base
CREATE TABLE knowledge_chunks (
  id INTEGER PRIMARY KEY,
  content TEXT NOT NULL,
  source TEXT,
  embedding BLOB NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- FTS for text search
CREATE VIRTUAL TABLE knowledge_fts USING fts5(content, source);

-- Indexes for performance
CREATE INDEX idx_chats_user ON chats(user_id);
CREATE INDEX idx_messages_chat ON messages(chat_id);
CREATE INDEX idx_research_user ON research_sessions(user_id);
CREATE INDEX idx_permissions_user ON tool_permissions(user_id);
CREATE INDEX idx_permissions_tool ON tool_permissions(tool_id);

-- Insert default tools
INSERT INTO tools (name, description, category, default_permission) VALUES
('terminal', 'Safe command execution with sandboxing', 'system', 'ask'),
('file_read', 'Read local files with path restrictions', 'system', 'ask'),
('file_write', 'Write to local files with restrictions', 'system', 'ask'),
('web_search', 'DuckDuckGo web search', 'web', 'allow'),
('kiwix', 'Offline wiki content access', 'knowledge', 'allow'),
('ollama_chat', 'Direct Ollama model interaction', 'ai', 'allow'),
('rag_search', 'Knowledge base retrieval', 'knowledge', 'allow'),
('embedding_gen', 'Generate text embeddings', 'ai', 'allow');