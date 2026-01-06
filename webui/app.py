from __future__ import annotations
import json
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import Database
from backend.auth import AuthManager, auth_manager
from backend.config import AutoConfig

APP_TITLE = "Router Phase 1 - Simple Chat"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:latest")

app = FastAPI(title=APP_TITLE)

# Mount static files
app.mount("/static", StaticFiles(directory="webui/static"), name="static")

# Security
security = HTTPBearer(auto_error=False)

# Database and services
db = Database()
config_manager = AutoConfig()

# Pydantic models
class ChatRequest(BaseModel):
    text: str

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    username: str
    profile: dict

# Auth dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token required")

    user = auth_manager.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return user

def _load_config() -> dict:
    return config_manager.load_config()

# Authentication endpoints
@app.post("/api/auth/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    user_id = auth_manager.create_user(request.username, request.password)
    if not user_id:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = auth_manager.authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=500, detail="Registration failed")

    access_token = auth_manager.create_access_token({"sub": user["username"], "user_id": user["id"]})
    return TokenResponse(access_token=access_token)

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    user = auth_manager.authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = auth_manager.create_access_token({"sub": user["username"], "user_id": user["id"]})
    return TokenResponse(access_token=access_token)

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

@app.get("/", response_class=HTMLResponse)
def home():
    config = _load_config()
    theme = config.get("theme", "dark")
    checked_light = 'checked' if theme == 'light' else ''
    checked_dark = 'checked' if theme == 'dark' else ''
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>""" + APP_TITLE + """</title>
    <link rel="stylesheet" href="/static/css/""" + theme + """.css">
    <style>
        .settings-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 2000; display: none; align-items: center; justify-content: center;
        }
        .settings-modal {
            background: var(--card-bg); color: var(--text-color); border: 1px solid var(--border-color); border-radius: 14px; width: 90%; max-width: 600px; max-height: 80%; overflow-y: auto; padding: 20px; position: relative;
        }
        .settings-modal h2 { margin-top: 0; }
        .settings-modal .close-btn { position: absolute; top: 10px; right: 10px; background: none; border: none; font-size: 20px; cursor: pointer; }
        .settings-section { margin-bottom: 20px; }
        .settings-section h3 { border-bottom: 1px solid var(--border-color); padding-bottom: 5px; }
        .sidebar {
            position: fixed; left: 0; top: 0; width: 300px; height: 100%; background: var(--card-bg); border-right: 1px solid var(--border-color); padding: 20px; box-shadow: 2px 0 5px rgba(0,0,0,0.1); transform: translateX(-100%); transition: transform 0.3s;
        }
        .sidebar.show { transform: translateX(0); }
        .sidebar h3 { margin-top: 0; }
        .sidebar .close-btn { position: absolute; top: 10px; right: 10px; background: none; border: none; font-size: 20px; cursor: pointer; }
        .sidebar-content { padding: 20px; }
        .sidebar-content h3 { margin-top: 0; }
        .sidebar-content ul { list-style: none; padding: 0; }
        .chat-item { padding: 8px; cursor: pointer; border-bottom: 1px solid var(--border-color); }
        .chat-item:hover { background: var(--card-bg); }
        .chat-item.active { background: var(--accent-color); color: white; }
        #newChatBtn { width: 100%; margin-bottom: 10px; }
        .msg { margin-bottom: 10px; padding: 10px; border-radius: 8px; }
        .msg.user { background: var(--accent-color); color: white; margin-left: 20%; }
        .msg.assistant { background: var(--card-bg); border: 1px solid var(--border-color); margin-right: 20%; }
        .msg-meta { font-size: 0.8em; opacity: 0.7; margin-top: 5px; }
        .view { display: none; }
        .view.active { display: block; }
        .nav-tabs { display: flex; margin-bottom: 10px; }
        .tab { flex: 1; padding: 8px; border: none; background: var(--card-bg); border-bottom: 2px solid transparent; cursor: pointer; }
        .tab.active { border-bottom-color: var(--accent-color); font-weight: bold; }
        .panel { display: none; }
        .panel.active { display: block; }
        .research-item { padding: 8px; cursor: pointer; border-bottom: 1px solid var(--border-color); }
        .research-item:hover { background: var(--card-bg); }
        .knowledge-item { padding: 8px; border-bottom: 1px solid var(--border-color); margin-bottom: 5px; }
        #toggleSidebar { position: fixed; top: 20px; left: 20px; z-index: 1000; }
        #settingsBtn { position: fixed; top: 20px; left: 70px; z-index: 1000; }
        .auth-section { display: none; }
        .auth-section.show { display: block; }
        .chat-section { display: none; }
        .chat-section.show { display: block; }
    </style>
</head>
<body>
    <div id="authSection" class="auth-section show">
        <div class="wrap">
            <div class="card">
                <h2>Login to """ + APP_TITLE + """</h2>
                <input type="text" id="username" placeholder="Username" style="width:100%; margin-bottom:10px;"><br>
                <input type="password" id="password" placeholder="Password" style="width:100%; margin-bottom:10px;"><br>
                <button class="btn" id="loginBtn">Login</button>
                <button class="btn" id="registerBtn">Register</button>
            </div>
        </div>
    </div>
    <div id="chatSection" class="chat-section">
        <button id="settingsBtn" class="btn">⚙️</button>
        <button id="toggleSidebar" class="btn">☰</button>
        <div class="settings-overlay" id="settingsOverlay">
            <div class="settings-modal">
                <button class="close-btn" id="closeSettings">×</button>
                <h2>Settings</h2>
            <div class="settings-section">
                <h3>Appearance</h3>
                <label><input type="radio" name="theme" value="light" """ + checked_light + """> Light Theme</label><br>
                <label><input type="radio" name="theme" value="dark" """ + checked_dark + """> Dark Theme</label>
                <br><label>Accent Color: <input type="color" id="accentColor" value="#007bff"></label>
            </div>
            <div class="settings-section">
                <h3>Research Settings</h3>
                <label>Time Limit (hours): <input type="number" id="timeLimit" min="1" max="720" value="24"></label><br>
                <label>Default Model: <select id="defaultModel">
                    <option value="llama3.2:latest">llama3.2:latest</option>
                    <option value="llama3.1:8b">llama3.1:8b</option>
                </select></label><br>
                <label>Max Memory Usage (GB): <input type="number" id="maxMemory" min="1" max="15" step="0.1" value="12"></label>
            </div>
            <div class="settings-section">
                <h3>Tool Permissions</h3>
                <label><input type="checkbox" id="allowWebSearch" checked> Allow Web Search</label><br>
                <label><input type="checkbox" id="allowFileAccess" checked> Allow File Access</label><br>
                <label><input type="checkbox" id="allowSystemTools"> Allow System Tools</label>
            </div>
            </div>
        </div>
        <div class="sidebar" id="sidebar">
            <button class="close-btn" id="closeSidebar">×</button>
            <div class="sidebar-content">
                <div class="nav-tabs">
                    <button id="chatTab" class="tab active">Chat</button>
                    <button id="researchTab" class="tab">Research</button>
                    <button id="ragTab" class="tab">RAG</button>
                </div>
                <div id="chatPanel" class="panel active">
                    <h3>Chats</h3>
                    <input type="text" id="chatSearch" placeholder="Search chats..." style="width:100%; margin-bottom:10px;">
                    <button id="newChatBtn">+ New Chat</button>
                    <ul id="chatList"></ul>
                </div>
                <div id="researchPanel" class="panel">
                    <h3>Research Sessions</h3>
                    <ul id="researchList"></ul>
                </div>
                <div id="ragPanel" class="panel">
                    <h3>RAG Management</h3>
                    <button id="addKnowledgeBtn">+ Add Knowledge</button>
                    <button id="maintenanceBtn">Run Maintenance</button>
                    <div id="knowledgeList"></div>
                </div>
            </div>
        </div>
    <div id="chatView" class="view active">
        <div class="wrap">
            <div class="card">
                <h2>Chat</h2>
                <div id="msgs" class="msgs"></div>
                <textarea id="prompt" placeholder="Type your message..." rows="3"></textarea>
                <div style="margin-top:10px;">
                    <button class="btn" id="shareBtnSidebar">📤 Share Conversation</button>
                    <button class="btn" id="sendBtn">Send</button>
                </div>
            </div>
        </div>
    </div>
    <div id="researchView" class="view">
        <div class="wrap">
            <div class="card">
                <h2>Research Dashboard</h2>
                <div id="researchControls">
                    <input type="text" id="researchTopic" placeholder="Enter research topic..." style="width:70%;">
                    <select id="researchDepth">
                        <option value="quick">Quick</option>
                        <option value="standard" selected>Standard</option>
                        <option value="deep">Deep</option>
                    </select>
                    <button class="btn" id="startResearchBtn">Start Research</button>
                </div>
                <div id="researchProgress" style="margin-top:20px; display:none;">
                    <div id="progressBar" style="width:100%; height:20px; background:#eee; border-radius:10px; overflow:hidden;">
                        <div id="progressFill" style="height:100%; background:var(--accent-color); width:0%; transition:width 0.3s;"></div>
                    </div>
                    <div id="progressText" style="margin-top:5px;">Initializing...</div>
                    <div id="agentStatus" style="margin-top:10px;"></div>
                    <button class="btn" id="stopResearchBtn" style="margin-top:10px;">Stop Research</button>
                </div>
                <div id="researchResults" style="margin-top:20px; display:none;">
                    <h3>Results</h3>
                    <div id="resultsContent"></div>
                </div>
            </div>
        </div>
    </div>
    </div>
    <script>
        const authSection = document.getElementById('authSection');
        const chatSection = document.getElementById('chatSection');
        const usernameEl = document.getElementById('username');
        const passwordEl = document.getElementById('password');
        const loginBtn = document.getElementById('loginBtn');
        const registerBtn = document.getElementById('registerBtn');
        const promptEl = document.getElementById('prompt');
        const msgsEl = document.getElementById('msgs');
        const sendBtn = document.getElementById('sendBtn');
        const settingsBtn = document.getElementById('settingsBtn');
        const settingsOverlay = document.getElementById('settingsOverlay');
        const closeSettings = document.getElementById('closeSettings');
        const toggleSidebar = document.getElementById('toggleSidebar');
        const sidebar = document.getElementById('sidebar');
        const closeSidebar = document.getElementById('closeSidebar');
        const shareBtnSidebar = document.getElementById('shareBtnSidebar');

        let accessToken = localStorage.getItem('accessToken');
        let currentChatId = null;
        let currentResearchTaskId = null;

        function showChat() {
            authSection.classList.remove('show');
            chatSection.classList.add('show');
        }

        function showAuth() {
            chatSection.classList.remove('show');
            authSection.classList.add('show');
        }

        async function loadChats(search = '') {
            try {
                const url = search ? `http://localhost:8000/api/chats/search?q=${encodeURIComponent(search)}` : 'http://localhost:8000/api/chats';
                const response = await fetch(url, {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                const chats = await response.json();
                renderChatList(chats);
            } catch(e) {
                console.error('Failed to load chats:', e);
            }
        }

        function renderChatList(chats) {
            const chatList = document.getElementById('chatList');
            chatList.innerHTML = '';
            chats.forEach(chat => {
                const li = document.createElement('li');
                li.className = 'chat-item';
                li.dataset.chatId = chat.id;
                li.textContent = chat.title;
                li.onclick = () => loadChat(chat.id);
                chatList.appendChild(li);
            });
        }

        async function createNewChat() {
            try {
                const response = await fetch('http://localhost:8000/api/chats', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                const data = await response.json();
                currentChatId = data.id;
                loadChats();
                clearMessages();
            } catch(e) {
                alert('Failed to create chat: ' + e.message);
            }
        }

        async function loadChat(chatId) {
            try {
                const response = await fetch(`http://localhost:8000/api/chats/${chatId}`, {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                const chat = await response.json();
                currentChatId = chat.id;
                renderMessages(chat.messages);
                // Update active chat in sidebar
                document.querySelectorAll('.chat-item').forEach(item => {
                    item.classList.toggle('active', item.dataset.chatId === chatId);
                });
            } catch(e) {
                alert('Failed to load chat: ' + e.message);
            }
        }

        function renderMessages(messages) {
            msgsEl.innerHTML = '';
            messages.forEach(msg => {
                const msgDiv = document.createElement('div');
                msgDiv.className = `msg ${msg.role}`;
                msgDiv.innerHTML = `<div class="msg-content">${msg.content}</div>`;
                if (msg.token_count) {
                    msgDiv.innerHTML += `<div class="msg-meta">Tokens: ${msg.token_count}</div>`;
                }
                msgsEl.appendChild(msgDiv);
            });
        }

        function clearMessages() {
            msgsEl.innerHTML = '';
        }

        // Research functions
        async function loadResearchSessions() {
            try {
                const response = await fetch('http://localhost:8000/api/research/sessions', {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                const data = await response.json();
                renderResearchList(data.sessions || []);
            } catch(e) {
                console.error('Failed to load research sessions:', e);
            }
        }

        function renderResearchList(sessions) {
            const researchList = document.getElementById('researchList');
            researchList.innerHTML = '';
            sessions.forEach(session => {
                const li = document.createElement('li');
                li.className = 'research-item';
                li.textContent = `${session.query} (${session.status})`;
                li.onclick = () => loadResearchSession(session.id);
                researchList.appendChild(li);
            });
        }

        async function loadResearchSession(taskId) {
            currentResearchTaskId = taskId;
            // Show progress and start monitoring
            document.getElementById('researchProgress').style.display = 'block';
            monitorResearchProgress();
        }

        async function startResearch() {
            const topic = document.getElementById('researchTopic').value.trim();
            const depth = document.getElementById('researchDepth').value;
            if (!topic) return;

            try {
                const response = await fetch('http://localhost:8000/api/research/start', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        topic: topic,
                        depth: depth
                    })
                });
                const data = await response.json();
                if (response.ok) {
                    currentResearchTaskId = data.task_id;
                    document.getElementById('researchProgress').style.display = 'block';
                    monitorResearchProgress();
                } else {
                    alert('Research start failed: ' + (data.error || 'Unknown error'));
                }
            } catch(e) {
                alert('Failed to start research: ' + e.message);
            }
        }

        async function monitorResearchProgress() {
            if (!currentResearchTaskId) return;

            try {
                const response = await fetch(`http://localhost:8000/api/research/${currentResearchTaskId}/status`, {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                const status = await response.json();

                // Update progress bar
                const progressFill = document.getElementById('progressFill');
                const progressText = document.getElementById('progressText');
                const agentStatus = document.getElementById('agentStatus');

                if (status.progress !== undefined) {
                    progressFill.style.width = `${status.progress}%`;
                    progressText.textContent = status.status || 'Running...';
                }

                if (status.agents) {
                    agentStatus.innerHTML = '<h4>Agent Status:</h4>' +
                        status.agents.map(agent => `<div>${agent.name}: ${agent.status}</div>`).join('');
                }

                if (status.status === 'completed' || status.status === 'failed') {
                    // Stop monitoring
                    return;
                }

                // Continue monitoring
                setTimeout(monitorResearchProgress, 2000);
            } catch(e) {
                console.error('Failed to get research status:', e);
            }
        }

        // Research event listeners
        document.getElementById('startResearchBtn').onclick = startResearch;
        document.getElementById('stopResearchBtn').onclick = async () => {
            if (currentResearchTaskId) {
                await fetch(`http://localhost:8000/api/research/${currentResearchTaskId}/stop`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                document.getElementById('researchProgress').style.display = 'none';
                currentResearchTaskId = null;
            }
        };

        // RAG functions
        async function loadKnowledge() {
            try {
                const response = await fetch('http://localhost:8000/api/rag/knowledge', {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                const knowledge = await response.json();
                renderKnowledgeList(knowledge);
            } catch(e) {
                console.error('Failed to load knowledge:', e);
            }
        }

        function renderKnowledgeList(knowledge) {
            const knowledgeList = document.getElementById('knowledgeList');
            knowledgeList.innerHTML = '<h4>Knowledge Base</h4>';
            knowledge.forEach(item => {
                const div = document.createElement('div');
                div.className = 'knowledge-item';
                div.innerHTML = `<strong>${item.source || 'Unknown'}</strong>: ${item.content.substring(0, 100)}...`;
                knowledgeList.appendChild(div);
            });
        }

        // RAG event listeners
        document.getElementById('addKnowledgeBtn').onclick = () => {
            const content = prompt('Enter knowledge content:');
            const source = prompt('Enter source:');
            if (content && source) {
                addKnowledge(content, source);
            }
        };

        document.getElementById('maintenanceBtn').onclick = async () => {
            try {
                await fetch('http://localhost:8000/api/rag/maintenance', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                alert('Maintenance completed');
                loadKnowledge();
            } catch(e) {
                alert('Maintenance failed: ' + e.message);
            }
        };

        async function addKnowledge(content, source) {
            try {
                await fetch('http://localhost:8000/api/rag/knowledge', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({content: content, source: source})
                });
                loadKnowledge();
            } catch(e) {
                alert('Failed to add knowledge: ' + e.message);
            }
        }

        // Tab switching
        const chatTab = document.getElementById('chatTab');
        const researchTab = document.getElementById('researchTab');
        const ragTab = document.getElementById('ragTab');
        const chatView = document.getElementById('chatView');
        const researchView = document.getElementById('researchView');
        const chatPanel = document.getElementById('chatPanel');
        const researchPanel = document.getElementById('researchPanel');
        const ragPanel = document.getElementById('ragPanel');

        chatTab.onclick = () => {
            chatTab.classList.add('active');
            researchTab.classList.remove('active');
            chatView.classList.add('active');
            researchView.classList.remove('active');
            chatPanel.classList.add('active');
            researchPanel.classList.remove('active');
        };

        researchTab.onclick = () => {
            researchTab.classList.add('active');
            chatTab.classList.remove('active');
            ragTab.classList.remove('active');
            researchView.classList.add('active');
            chatView.classList.remove('active');
            researchPanel.classList.add('active');
            chatPanel.classList.remove('active');
            ragPanel.classList.remove('active');
            loadResearchSessions();
        };

        ragTab.onclick = () => {
            ragTab.classList.add('active');
            chatTab.classList.remove('active');
            researchTab.classList.remove('active');
            ragPanel.classList.add('active');
            chatPanel.classList.remove('active');
            researchPanel.classList.remove('active');
            loadKnowledge();
        };

        // Search functionality
        const chatSearch = document.getElementById('chatSearch');
        chatSearch.addEventListener('input', (e) => {
            loadChats(e.target.value);
        });

        if (accessToken) {
            showChat();
            loadChats();
        }

        loginBtn.onclick = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        username: usernameEl.value,
                        password: passwordEl.value
                    })
                });
                const data = await response.json();
                if (response.ok) {
                    accessToken = data.access_token;
                    localStorage.setItem('accessToken', accessToken);
                    showChat();
                    loadChats();
                } else {
                    alert(data.detail);
                }
            } catch(e) {
                alert('Login failed: ' + e.message);
            }
        };

        registerBtn.onclick = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/auth/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        username: usernameEl.value,
                        password: passwordEl.value
                    })
                });
                const data = await response.json();
                if (response.ok) {
                    accessToken = data.access_token;
                    localStorage.setItem('accessToken', accessToken);
                    showChat();
                    loadChats();
                } else {
                    alert(data.detail);
                }
            } catch(e) {
                alert('Registration failed: ' + e.message);
            }
        };

        settingsBtn.onclick = () => {
            settingsOverlay.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        };

        closeSettings.onclick = () => {
            settingsOverlay.style.display = 'none';
            document.body.style.overflow = '';
        };

        settingsOverlay.onclick = (e) => {
            if (e.target === settingsOverlay) {
                settingsOverlay.style.display = 'none';
                document.body.style.overflow = '';
            }
        };

        toggleSidebar.onclick = () => {
            sidebar.classList.toggle('show');
        };

        closeSidebar.onclick = () => {
            sidebar.classList.remove('show');
        };

        shareBtnSidebar.onclick = async () => {
            try {
                const r = await fetch('http://localhost:8000/api/share', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                const data = await r.json();
                await navigator.clipboard.writeText(data.link);
                alert('Share link copied!');
            } catch(e) {
                alert('Error: ' + e.message);
            }
        };

        themeRadios.forEach(radio => {
            radio.addEventListener('change', async (e) => {
                const newTheme = e.target.value;
                try {
                    await fetch('http://localhost:8000/api/config', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${accessToken}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({theme: newTheme})
                    });
                    location.reload();
                } catch(e) {
                    alert('Error saving theme: ' + e.message);
                }
            });
        });
                    location.reload();
                } catch(e) {
                    alert('Error saving theme: ' + e.message);
                }
            });
        });

        sendBtn.onclick = async () => {
            const message = promptEl.value.trim();
            if (!message) return;

            // Add user message to UI
            const userMsgDiv = document.createElement('div');
            userMsgDiv.className = 'msg user';
            userMsgDiv.textContent = message;
            msgsEl.appendChild(userMsgDiv);
            const currentMessage = message;
            promptEl.value = '';

            try {
                // Send to chat API
                const response = await fetch('http://localhost:8000/api/chat', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: currentMessage,
                        chat_id: currentChatId
                    })
                });

                const data = await response.json();
                if (response.ok) {
                    // Add AI response to UI
                    const aiMsgDiv = document.createElement('div');
                    aiMsgDiv.className = 'msg assistant';
                    aiMsgDiv.textContent = data.response;
                    msgsEl.appendChild(aiMsgDiv);

                    // If no chat selected, create one and add messages
                    if (!currentChatId) {
                        const chatResponse = await fetch('http://localhost:8000/api/chats', {
                            method: 'POST',
                            headers: {
                                'Authorization': `Bearer ${accessToken}`
                            }
                        });
                        const chatData = await chatResponse.json();
                        currentChatId = chatData.id;
                        loadChats();
                    }
                } else {
                    alert('Chat error: ' + (data.error || 'Unknown error'));
                }

            } catch(e) {
                alert('Failed to send message: ' + e.message);
            }
        };

        promptEl.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendBtn.click();
            }
        });
    </script>
</body>
</html>
"""
    return html

@app.post("/api/share")
def api_share(request: Request, current_user: dict = Depends(get_current_user)):
    base_url = str(request.base_url).rstrip('/')
    link = f"{base_url}/share"
    return {"link": link}

@app.post("/api/config")
def api_config(data: dict, current_user: dict = Depends(get_current_user)):
    # Update user settings in database
    import sqlite3
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        for key, value in data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO settings (user_id, key, value)
                VALUES (?, ?, ?)
            """, (current_user["id"], key, json.dumps(value)))
        conn.commit()
    return {"status": "ok"}

@app.get("/api/config")
def get_config(current_user: dict = Depends(get_current_user)):
    # Get user settings from database
    import sqlite3
    config = {}
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings WHERE user_id = ?", (current_user["id"],))
        for row in cursor.fetchall():
            key, value_json = row
            config[key] = json.loads(value_json)
    return config