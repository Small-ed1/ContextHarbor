from __future__ import annotations
import json
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import Database
from backend.auth import AuthManager, auth_manager
from backend.config import AutoConfig

APP_TITLE = "Router Phase 1 - Modern UI"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:latest")

app = FastAPI(title=APP_TITLE)

# Templates
templates = Jinja2Templates(directory="webui/templates")

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

# New UI Phase: Modern Component-Based Architecture

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request, "mode": "login"})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request, "mode": "register"})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page():
    return templates.TemplateResponse("dashboard.html")

@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return templates.TemplateResponse("chat.html")

@app.get("/research", response_class=HTMLResponse)
def research_page():
    return templates.TemplateResponse("research.html")

@app.get("/knowledge", response_class=HTMLResponse)
def knowledge_page():
    return templates.TemplateResponse("knowledge.html")

@app.get("/settings", response_class=HTMLResponse)
def settings_page():
    return modern_settings_page()

@app.get("/profile", response_class=HTMLResponse)
def profile_page():
    return modern_profile_page()

@app.get("/help", response_class=HTMLResponse)
def help_page():
    return modern_help_page()

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return modern_admin_page()

@app.get("/search", response_class=HTMLResponse)
def search_page():
    return modern_search_page()

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

# Modern page functions

def modern_home_page():
    """Modern landing page with feature showcase"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Router Phase 1 - AI-Powered Research Assistant</title>
    <link rel="stylesheet" href="/static/css/modern.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="landing-page">
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-brand">
                <h1>Router Phase 1</h1>
                <span class="tagline">AI-Powered Research Assistant</span>
            </div>
            <div class="nav-links">
                <a href="#features" class="nav-link">Features</a>
                <a href="#demo" class="nav-link">Demo</a>
                <a href="/login" class="btn btn-primary">Get Started</a>
            </div>
        </div>
    </nav>

    <section class="hero">
        <div class="hero-container">
            <div class="hero-content">
                <h1 class="hero-title">Intelligent Research<br>at Your Fingertips</h1>
                <p class="hero-subtitle">Experience the future of AI-assisted research with multi-agent systems, knowledge graphs, and seamless collaboration.</p>
                <div class="hero-actions">
                    <a href="/register" class="btn btn-primary btn-lg">Start Free Trial</a>
                    <a href="#demo" class="btn btn-secondary btn-lg">Watch Demo</a>
                </div>
            </div>
            <div class="hero-visual">
                <div class="mockup-container">
                    <div class="mockup-screen">
                        <div class="mockup-header">
                            <div class="mockup-dots">
                                <span class="dot red"></span>
                                <span class="dot yellow"></span>
                                <span class="dot green"></span>
                            </div>
                            <div class="mockup-title">Research Dashboard</div>
                        </div>
                        <div class="mockup-content">
                            <div class="mockup-sidebar">
                                <div class="mockup-nav-item active">📊 Dashboard</div>
                                <div class="mockup-nav-item">💬 Chat</div>
                                <div class="mockup-nav-item">🔬 Research</div>
                                <div class="mockup-nav-item">📚 Knowledge</div>
                            </div>
                            <div class="mockup-main">
                                <div class="mockup-card">
                                    <h3>Active Research Sessions</h3>
                                    <div class="mockup-progress">
                                        <div class="progress-bar" style="width: 75%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section id="features" class="features">
        <div class="container">
            <div class="section-header">
                <h2>Powerful Features for Modern Research</h2>
                <p>Everything you need to conduct thorough, efficient research with AI assistance.</p>
            </div>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <h3>Multi-Agent Research</h3>
                    <p>Deploy specialized AI agents for different research tasks, from data collection to analysis and synthesis.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📚</div>
                    <h3>Knowledge Graphs</h3>
                    <p>Build and explore interconnected knowledge bases with visual graph representations and semantic search.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💬</div>
                    <h3>Intelligent Chat</h3>
                    <p>Converse naturally with AI assistants that understand context and can execute complex research tasks.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔍</div>
                    <h3>Advanced Search</h3>
                    <p>Search across multiple sources with intelligent filtering, ranking, and result synthesis.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3>Analytics Dashboard</h3>
                    <p>Track research progress, analyze patterns, and gain insights from your research activities.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔒</div>
                    <h3>Secure & Private</h3>
                    <p>Local-first architecture ensures your research data stays private and secure.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="demo" class="demo">
        <div class="container">
            <div class="section-header">
                <h2>See It In Action</h2>
                <p>Experience the power of Router Phase 1 through interactive demonstrations.</p>
            </div>
            <div class="demo-grid">
                <div class="demo-item">
                    <h3>🚀 Quick Start</h3>
                    <p>Get up and running in minutes with our guided setup process.</p>
                    <a href="/register" class="btn btn-primary">Try Now</a>
                </div>
                <div class="demo-item">
                    <h3>📖 Documentation</h3>
                    <p>Comprehensive guides and API documentation for advanced usage.</p>
                    <a href="/help" class="btn btn-secondary">Learn More</a>
                </div>
                <div class="demo-item">
                    <h3>🎯 Use Cases</h3>
                    <p>Explore real-world applications and success stories.</p>
                    <a href="#features" class="btn btn-secondary">Explore</a>
                </div>
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h4>Router Phase 1</h4>
                    <p>AI-powered research assistant for the modern researcher.</p>
                </div>
                <div class="footer-section">
                    <h4>Product</h4>
                    <a href="#features">Features</a>
                    <a href="/help">Documentation</a>
                    <a href="/admin">Admin</a>
                </div>
                <div class="footer-section">
                    <h4>Support</h4>
                    <a href="/help">Help Center</a>
                    <a href="#demo">Demo</a>
                    <a href="/settings">Settings</a>
                </div>
                <div class="footer-section">
                    <h4>Legal</h4>
                    <a href="#">Privacy</a>
                    <a href="#">Terms</a>
                    <a href="#">Security</a>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2026 Router Phase 1. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="/static/js/modern.js"></script>
</body>
</html>"""

def modern_auth_page(mode: str):
    """Modern authentication page with animations"""
    title = "Login" if mode == "login" else "Register"
    action = "/api/auth/login" if mode == "login" else "/api/auth/register"
    switch_text = "Don't have an account?" if mode == "login" else "Already have an account?"
    switch_link = "/register" if mode == "login" else "/login"
    switch_action = "Register" if mode == "login" else "Login"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} - Router Phase 1</title>
    <link rel="stylesheet" href="/static/css/modern.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="auth-page">
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <h1>Welcome to Router Phase 1</h1>
                <p>Your AI-powered research companion</p>
            </div>

            <form class="auth-form" id="authForm">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>

                <button type="submit" class="btn btn-primary btn-full">
                    {title}
                </button>
            </form>

            <div class="auth-divider">
                <span>or</span>
            </div>

            <div class="social-auth">
                <button class="btn btn-social btn-google">
                    <span class="social-icon">G</span>
                    Continue with Google
                </button>
                <button class="btn btn-social btn-github">
                    <span class="social-icon">GH</span>
                    Continue with GitHub
                </button>
            </div>

            <div class="auth-footer">
                <p>{switch_text} <a href="{switch_link}">{switch_action}</a></p>
            </div>
        </div>

        <div class="auth-features">
            <div class="feature-item">
                <div class="feature-icon">🚀</div>
                <h3>Quick Setup</h3>
                <p>Get started in under 5 minutes</p>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🔒</div>
                <h3>Secure</h3>
                <p>Your data stays local and private</p>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🤖</div>
                <h3>AI-Powered</h3>
                <p>Advanced AI agents for research</p>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('authForm').addEventListener('submit', async (e) => {{
            e.preventDefault();

            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);

            try {{
                const response = await fetch('{action}', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify(data)
                }});

                const result = await response.json();

                if (response.ok) {{
                    localStorage.setItem('accessToken', result.access_token);
                    window.location.href = '/dashboard';
                }} else {{
                    alert(result.detail || 'Authentication failed');
                }}
            }} catch (error) {{
                alert('Network error: ' + error.message);
            }}
        }});
    </script>
</body>
</html>"""

def modern_dashboard_page():
    """Comprehensive dashboard with stats and activity"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Dashboard - Router Phase 1</title>
    <link rel="stylesheet" href="/static/css/modern.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="dashboard-page">
    <div class="app-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>Router Phase 1</h2>
            </div>
            <ul class="sidebar-nav">
                <li class="nav-item active">
                    <a href="/dashboard">
                        <span class="nav-icon">📊</span>
                        Dashboard
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/chat">
                        <span class="nav-icon">💬</span>
                        Chat
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/research">
                        <span class="nav-icon">🔬</span>
                        Research
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/knowledge">
                        <span class="nav-icon">📚</span>
                        Knowledge
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/settings">
                        <span class="nav-icon">⚙️</span>
                        Settings
                    </a>
                </li>
            </ul>
        </nav>

        <main class="main-content">
            <header class="page-header">
                <h1>Dashboard</h1>
                <div class="header-actions">
                    <button class="btn btn-primary" id="newChatBtn">
                        <span class="btn-icon">+</span>
                        New Chat
                    </button>
                    <button class="btn btn-secondary" id="newResearchBtn">
                        <span class="btn-icon">🔬</span>
                        New Research
                    </button>
                </div>
            </header>

            <div class="dashboard-grid">
                <div class="dashboard-card stats-card">
                    <h3>Quick Stats</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value" id="chatCount">0</div>
                            <div class="stat-label">Total Chats</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="researchCount">0</div>
                            <div class="stat-label">Research Sessions</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="knowledgeCount">0</div>
                            <div class="stat-label">Knowledge Items</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="tokenCount">0</div>
                            <div class="stat-label">Tokens Used</div>
                        </div>
                    </div>
                </div>

                <div class="dashboard-card recent-activity">
                    <h3>Recent Activity</h3>
                    <div class="activity-list" id="recentActivity">
                        <div class="activity-item loading">
                            <div class="activity-icon">⏳</div>
                            <div class="activity-content">
                                <div class="activity-title">Loading activity...</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="dashboard-card quick-actions">
                    <h3>Quick Actions</h3>
                    <div class="action-buttons">
                        <button class="action-btn" onclick="startChat()">
                            <span class="action-icon">💬</span>
                            <span class="action-text">Start Chat</span>
                        </button>
                        <button class="action-btn" onclick="startResearch()">
                            <span class="action-icon">🔬</span>
                            <span class="action-text">Begin Research</span>
                        </button>
                        <button class="action-btn" onclick="addKnowledge()">
                            <span class="action-icon">📚</span>
                            <span class="action-text">Add Knowledge</span>
                        </button>
                        <button class="action-btn" onclick="viewSettings()">
                            <span class="action-icon">⚙️</span>
                            <span class="action-text">Settings</span>
                        </button>
                    </div>
                </div>

                <div class="dashboard-card active-research">
                    <h3>Active Research</h3>
                    <div class="research-list" id="activeResearch">
                        <div class="no-research">
                            <span class="no-research-icon">🔬</span>
                            <p>No active research sessions</p>
                            <button class="btn btn-primary btn-sm" onclick="startResearch()">Start Research</button>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        // Dashboard functionality
        document.addEventListener('DOMContentLoaded', function() {{
            loadDashboardData();
            setupEventListeners();
        }});

        function setupEventListeners() {{
            document.getElementById('newChatBtn').addEventListener('click', startChat);
            document.getElementById('newResearchBtn').addEventListener('click', startResearch);
        }}

        async function loadDashboardData() {{
            const token = localStorage.getItem('accessToken');
            if (!token) {{
                window.location.href = '/login';
                return;
            }}

            try {{
                // Load stats
                const statsResponse = await fetch('/api/dashboard/stats', {{
                    headers: {{ 'Authorization': `Bearer ${{token}}` }}
                }});
                if (statsResponse.ok) {{
                    const stats = await statsResponse.json();
                    updateStats(stats);
                }}

                // Load recent activity
                const activityResponse = await fetch('/api/dashboard/activity', {{
                    headers: {{ 'Authorization': `Bearer ${{token}}` }}
                }});
                if (activityResponse.ok) {{
                    const activity = await activityResponse.json();
                    updateActivity(activity);
                }}

                // Load active research
                const researchResponse = await fetch('/api/research/sessions', {{
                    headers: {{ 'Authorization': `Bearer ${{token}}` }}
                }});
                if (researchResponse.ok) {{
                    const research = await researchResponse.json();
                    updateActiveResearch(research.sessions || []);
                }}

            }} catch (error) {{
                console.error('Failed to load dashboard data:', error);
            }}
        }}

        function updateStats(stats) {{
            document.getElementById('chatCount').textContent = stats.chats || 0;
            document.getElementById('researchCount').textContent = stats.research || 0;
            document.getElementById('knowledgeCount').textContent = stats.knowledge || 0;
            document.getElementById('tokenCount').textContent = stats.tokens || 0;
        }}

        function updateActivity(activities) {{
            const container = document.getElementById('recentActivity');
            container.innerHTML = '';

            if (activities.length === 0) {{
                container.innerHTML = '<div class="no-activity">No recent activity</div>';
                return;
            }}

            activities.forEach(activity => {{
                const item = document.createElement('div');
                item.className = 'activity-item';
                item.innerHTML = `
                    <div class="activity-icon">${{getActivityIcon(activity.type)}}</div>
                    <div class="activity-content">
                        <div class="activity-title">${{activity.title}}</div>
                        <div class="activity-time">${{formatTime(activity.timestamp)}}</div>
                    </div>
                `;
                container.appendChild(item);
            }});
        }}

        function updateActiveResearch(sessions) {{
            const container = document.getElementById('activeResearch');
            const activeSessions = sessions.filter(s => s.status === 'running' || s.status === 'in_progress');

            if (activeSessions.length === 0) return;

            container.innerHTML = '';
            activeSessions.forEach(session => {{
                const item = document.createElement('div');
                item.className = 'research-item';
                item.innerHTML = `
                    <div class="research-title">${{session.query}}</div>
                    <div class="research-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${{session.progress || 0}}%"></div>
                        </div>
                        <span class="progress-text">${{session.status}}</span>
                    </div>
                `;
                container.appendChild(item);
            }});
        }}

        function getActivityIcon(type) {{
            const icons = {{
                'chat': '💬',
                'research': '🔬',
                'knowledge': '📚',
                'settings': '⚙️'
            }};
            return icons[type] || '📝';
        }}

        function formatTime(timestamp) {{
            const date = new Date(timestamp);
            const now = new Date();
            const diff = now - date;
            const minutes = Math.floor(diff / 60000);

            if (minutes < 1) return 'Just now';
            if (minutes < 60) return `${{minutes}}m ago`;
            const hours = Math.floor(minutes / 60);
            if (hours < 24) return `${{hours}}h ago`;
            return date.toLocaleDateString();
        }}

        function startChat() {{
            window.location.href = '/chat';
        }}

        function startResearch() {{
            window.location.href = '/research';
        }}

        function addKnowledge() {{
            window.location.href = '/knowledge';
        }}

        function viewSettings() {{
            window.location.href = '/settings';
        }}
    </script>
</body>
</html>"""

def modern_chat_page():
    """Advanced chat interface with modern features"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Chat - Router Phase 1</title>
    <link rel="stylesheet" href="/static/css/modern.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="chat-page">
    <div class="app-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-toggle" id="sidebarToggle">☰</div>
                <h2>Chats</h2>
                <button class="btn btn-primary btn-sm" id="newChatBtn">+ New</button>
            </div>
            <div class="chat-list" id="chatList">
                <div class="chat-list-loading">Loading chats...</div>
            </div>
        </nav>

        <main class="main-content">
            <div class="chat-header">
                <div class="chat-title">
                    <h1 id="currentChatTitle">Select a chat or start new</h1>
                </div>
                <div class="chat-actions">
                    <button class="btn btn-secondary" id="shareChatBtn">📤 Share</button>
                    <button class="btn btn-secondary" id="exportChatBtn">💾 Export</button>
                    <button class="btn btn-secondary" id="deleteChatBtn">🗑️ Delete</button>
                </div>
            </div>

            <div class="chat-messages" id="messagesContainer">
                <div class="welcome-message">
                    <div class="welcome-content">
                        <h2>Welcome to Router Phase 1 Chat</h2>
                        <p>Start a conversation with our AI assistant. Ask questions, request research, or explore knowledge.</p>
                        <div class="quick-prompts">
                            <button class="prompt-btn" onclick="sendQuickPrompt('Hello! Can you help me with research?')">🤝 Get Started</button>
                            <button class="prompt-btn" onclick="sendQuickPrompt('What can you help me with today?')">❓ What can you do?</button>
                            <button class="prompt-btn" onclick="sendQuickPrompt('Show me some examples of your capabilities')">💡 Show Examples</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="chat-input-area">
                <div class="input-container">
                    <textarea
                        id="messageInput"
                        placeholder="Type your message... (Shift+Enter for new line)"
                        rows="1"
                        maxlength="10000"
                    ></textarea>
                    <div class="input-actions">
                        <button class="btn btn-secondary" id="attachBtn" title="Attach file">
                            📎
                        </button>
                        <button class="btn btn-primary" id="sendBtn">
                            <span class="send-icon">➤</span>
                            Send
                        </button>
                    </div>
                </div>
                <div class="input-footer">
                    <span class="char-count" id="charCount">0/10000</span>
                    <div class="typing-indicator" id="typingIndicator" style="display: none;">
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                        <span>AI is typing...</span>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- Message Actions Modal -->
    <div class="modal" id="messageModal" style="display: none;">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Message Options</h3>
                <button class="modal-close" onclick="closeMessageModal()">×</button>
            </div>
            <div class="modal-body" id="messageModalBody">
                <!-- Message content will be inserted here -->
            </div>
        </div>
    </div>

    <script>
        let currentChatId = null;
        let accessToken = localStorage.getItem('accessToken');
        let messageHistory = [];

        document.addEventListener('DOMContentLoaded', function() {{
            if (!accessToken) {{
                window.location.href = '/login';
                return;
            }}

            initializeChat();
            setupEventListeners();
            loadChats();
        }});

        function initializeChat() {{
            if (currentChatId) {{
                loadChat(currentChatId);
            }}
        }}

        function setupEventListeners() {{
            // Message input
            const messageInput = document.getElementById('messageInput');
            messageInput.addEventListener('input', updateCharCount);
            messageInput.addEventListener('keydown', handleKeyDown);

            // Send button
            document.getElementById('sendBtn').addEventListener('click', sendMessage);

            // Chat management
            document.getElementById('newChatBtn').addEventListener('click', createNewChat);
            document.getElementById('shareChatBtn').addEventListener('click', shareChat);
            document.getElementById('exportChatBtn').addEventListener('click', exportChat);
            document.getElementById('deleteChatBtn').addEventListener('click', deleteChat);

            // Sidebar
            document.getElementById('sidebarToggle').addEventListener('click', toggleSidebar);

            // Attach file
            document.getElementById('attachBtn').addEventListener('click', attachFile);
        }}

        function updateCharCount() {{
            const input = document.getElementById('messageInput');
            const count = document.getElementById('charCount');
            count.textContent = `${{input.value.length}}/10000`;
        }}

        function handleKeyDown(e) {{
            if (e.key === 'Enter' && !e.shiftKey) {{
                e.preventDefault();
                sendMessage();
            }}
        }}

        async function loadChats() {{
            try {{
                const response = await fetch('/api/chats', {{
                    headers: {{ 'Authorization': `Bearer ${{accessToken}}` }}
                }});

                if (response.ok) {{
                    const chats = await response.json();
                    renderChatList(chats);
                }}
            }} catch (error) {{
                console.error('Failed to load chats:', error);
            }}
        }}

        function renderChatList(chats) {{
            const container = document.getElementById('chatList');
            container.innerHTML = '';

            if (chats.length === 0) {{
                container.innerHTML = '<div class="no-chats">No chats yet. Create your first chat!</div>';
                return;
            }}

            chats.forEach(chat => {{
                const chatItem = document.createElement('div');
                chatItem.className = `chat-item ${{currentChatId === chat.id ? 'active' : ''}}`;
                chatItem.onclick = () => selectChat(chat.id);

                chatItem.innerHTML = `
                    <div class="chat-item-title">${{chat.title || 'Untitled Chat'}}</div>
                    <div class="chat-item-meta">
                        <span class="chat-item-date">${{formatChatDate(chat.created_at)}}</span>
                        <span class="chat-item-count">${{chat.message_count || 0}} messages</span>
                    </div>
                `;

                container.appendChild(chatItem);
            }});
        }}

        function formatChatDate(dateString) {{
            const date = new Date(dateString);
            const now = new Date();
            const diff = now - date;
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));

            if (days === 0) return 'Today';
            if (days === 1) return 'Yesterday';
            if (days < 7) return `${{days}} days ago`;
            return date.toLocaleDateString();
        }}

        async function selectChat(chatId) {{
            currentChatId = chatId;
            await loadChat(chatId);

            // Update UI
            document.querySelectorAll('.chat-item').forEach(item => {{
                item.classList.remove('active');
            }});
            event.currentTarget.classList.add('active');
        }}

        async function loadChat(chatId) {{
            try {{
                const response = await fetch(`/api/chats/${{chatId}}`, {{
                    headers: {{ 'Authorization': `Bearer ${{accessToken}}` }}
                }});

                if (response.ok) {{
                    const chat = await response.json();
                    renderMessages(chat.messages || []);
                    updateChatTitle(chat.title || 'Untitled Chat');
                    messageHistory = chat.messages || [];
                }}
            }} catch (error) {{
                console.error('Failed to load chat:', error);
            }}
        }}

        function renderMessages(messages) {{
            const container = document.getElementById('messagesContainer');
            container.innerHTML = '';

            if (messages.length === 0) {{
                container.innerHTML = `
                    <div class="welcome-message">
                        <div class="welcome-content">
                            <h2>Welcome to Router Phase 1 Chat</h2>
                            <p>Start a conversation with our AI assistant. Ask questions, request research, or explore knowledge.</p>
                            <div class="quick-prompts">
                                <button class="prompt-btn" onclick="sendQuickPrompt('Hello! Can you help me with research?')">🤝 Get Started</button>
                                <button class="prompt-btn" onclick="sendQuickPrompt('What can you help me with today?')">❓ What can you do?</button>
                                <button class="prompt-btn" onclick="sendQuickPrompt('Show me some examples of your capabilities')">💡 Show Examples</button>
                            </div>
                        </div>
                    </div>
                `;
                return;
            }}

            messages.forEach((message, index) => {{
                const messageEl = createMessageElement(message, index);
                container.appendChild(messageEl);
            }});

            // Scroll to bottom
            container.scrollTop = container.scrollHeight;
        }}

        function createMessageElement(message, index) {{
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${{message.role}}`;
            messageDiv.dataset.messageId = index;

            messageDiv.innerHTML = `
                <div class="message-avatar">
                    ${{message.role === 'user' ? '👤' : '🤖'}}
                </div>
                <div class="message-content">
                    <div class="message-text">${{formatMessageText(message.content)}}</div>
                    <div class="message-meta">
                        <span class="message-time">${{formatMessageTime(message.timestamp)}}</span>
                        ${{message.token_count ? `<span class="token-count">${{message.token_count}} tokens</span>` : ''}}
                        <button class="message-actions-btn" onclick="showMessageActions(${{index}})">⋯</button>
                    </div>
                </div>
            `;

            return messageDiv;
        }}

        function formatMessageText(text) {{
            // Basic markdown-like formatting
            return text
                .replace(/\\n/g, '<br>')
                .replace(/```([\\s\\S]*?)```/g, '<pre><code>$1</code></pre>')
                .replace(/`([^`]+)`/g, '<code>$1</code>')
                .replace(/\\*\\*([^\\*\\*]+)\\*\\*/g, '<strong>$1</strong>')
                .replace(/\\*([^\\*]+)\\*/g, '<em>$1</em>');
        }}

        function formatMessageTime(timestamp) {{
            if (!timestamp) return '';
            const date = new Date(timestamp);
            return date.toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit'}});
        }}

        async function sendMessage() {{
            const input = document.getElementById('messageInput');
            const message = input.value.trim();

            if (!message) return;

            // Create chat if none exists
            if (!currentChatId) {{
                await createNewChat();
            }}

            // Add user message to UI
            const userMessage = {{
                role: 'user',
                content: message,
                timestamp: new Date().toISOString()
            }};

            messageHistory.push(userMessage);
            renderMessages(messageHistory);
            input.value = '';

            // Show typing indicator
            showTypingIndicator();

            try {{
                const response = await fetch('/api/chat', {{
                    method: 'POST',
                    headers: {{
                        'Authorization': `Bearer ${{accessToken}}`,
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        message: message,
                        chat_id: currentChatId,
                        history: messageHistory.slice(-10) // Last 10 messages for context
                    }})
                }});

                hideTypingIndicator();

                if (response.ok) {{
                    const result = await response.json();

                    const aiMessage = {{
                        role: 'assistant',
                        content: result.response,
                        timestamp: new Date().toISOString(),
                        token_count: result.token_count
                    }};

                    messageHistory.push(aiMessage);
                    renderMessages(messageHistory);

                    // Save to chat
                    await saveMessageToChat(currentChatId, userMessage);
                    await saveMessageToChat(currentChatId, aiMessage);

                }} else {{
                    const error = await response.json();
                    alert('Chat error: ' + (error.error || 'Unknown error'));
                }}

            }} catch (error) {{
                hideTypingIndicator();
                alert('Network error: ' + error.message);
            }}
        }}

        function showTypingIndicator() {{
            document.getElementById('typingIndicator').style.display = 'flex';
        }}

        function hideTypingIndicator() {{
            document.getElementById('typingIndicator').style.display = 'none';
        }}

        async function createNewChat() {{
            try {{
                const response = await fetch('/api/chats', {{
                    method: 'POST',
                    headers: {{ 'Authorization': `Bearer ${{accessToken}}` }}
                }});

                if (response.ok) {{
                    const chat = await response.json();
                    currentChatId = chat.id;
                    messageHistory = [];
                    renderMessages([]);
                    updateChatTitle('New Chat');
                    loadChats();
                }}
            }} catch (error) {{
                console.error('Failed to create chat:', error);
            }}
        }}

        async function saveMessageToChat(chatId, message) {{
            try {{
                await fetch(`/api/chats/${{chatId}}/messages`, {{
                    method: 'POST',
                    headers: {{
                        'Authorization': `Bearer ${{accessToken}}`,
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify(message)
                }});
            }} catch (error) {{
                console.error('Failed to save message:', error);
            }}
        }}

        function updateChatTitle(title) {{
            document.getElementById('currentChatTitle').textContent = title;
        }}

        function sendQuickPrompt(prompt) {{
            document.getElementById('messageInput').value = prompt;
            sendMessage();
        }}

        function showMessageActions(messageIndex) {{
            const message = messageHistory[messageIndex];
            const modal = document.getElementById('messageModal');
            const body = document.getElementById('messageModalBody');

            body.innerHTML = `
                <div class="message-actions">
                    <button onclick="copyMessage(${{messageIndex}})">📋 Copy</button>
                    <button onclick="regenerateMessage(${{messageIndex}})">🔄 Regenerate</button>
                    <button onclick="editMessage(${{messageIndex}})">✏️ Edit</button>
                    <button onclick="deleteMessage(${{messageIndex}})" class="danger">🗑️ Delete</button>
                </div>
                <div class="message-preview">
                    <strong>${{message.role === 'user' ? 'You' : 'Assistant'}}:</strong>
                    <p>${{message.content.substring(0, 200)}}${message.content.length > 200 ? '...' : ''}</p>
                </div>
            `;

            modal.style.display = 'flex';
        }}

        function closeMessageModal() {{
            document.getElementById('messageModal').style.display = 'none';
        }}

        function toggleSidebar() {{
            document.querySelector('.sidebar').classList.toggle('collapsed');
        }}

        function attachFile() {{
            // Placeholder for file attachment
            alert('File attachment coming soon!');
        }}

        // Placeholder functions
        function copyMessage(index) {{
            const message = messageHistory[index];
            navigator.clipboard.writeText(message.content);
            closeMessageModal();
        }}

        function shareChat() {{ alert('Share functionality coming soon!'); }}
        function exportChat() {{ alert('Export functionality coming soon!'); }}
        function deleteChat() {{ alert('Delete functionality coming soon!'); }}
        function regenerateMessage(index) {{ alert('Regenerate functionality coming soon!'); }}
        function editMessage(index) {{ alert('Edit functionality coming soon!'); }}
        function deleteMessage(index) {{ alert('Delete functionality coming soon!'); }}
    </script>
</body>
</html>"""

# Placeholder functions for other pages



def modern_settings_page():
    """Settings hub with comprehensive options"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Settings - Router Phase 1</title>
    <link rel="stylesheet" href="/static/css/modern.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="settings-page">
    <div class="app-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>Settings</h2>
            </div>
            <ul class="sidebar-nav">
                <li class="nav-item active">
                    <a href="/settings">
                        <span class="nav-icon">🎨</span>
                        Appearance
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/settings/account">
                        <span class="nav-icon">👤</span>
                        Account
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/settings/research">
                        <span class="nav-icon">🔬</span>
                        Research
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/settings/privacy">
                        <span class="nav-icon">🔒</span>
                        Privacy & Security
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/settings/integrations">
                        <span class="nav-icon">🔗</span>
                        Integrations
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/settings/advanced">
                        <span class="nav-icon">⚙️</span>
                        Advanced
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/settings/backups">
                        <span class="nav-icon">💾</span>
                        Backups
                    </a>
                </li>
            </ul>
        </nav>

        <main class="main-content">
            <header class="page-header">
                <h1>Settings</h1>
                <div class="header-actions">
                    <button class="btn btn-secondary" id="resetSettingsBtn">
                        <span class="btn-icon">🔄</span>
                        Reset to Defaults
                    </button>
                    <button class="btn btn-primary" id="saveSettingsBtn">
                        <span class="btn-icon">💾</span>
                        Save Changes
                    </button>
                </div>
            </header>

            <div class="settings-notifications" id="settingsNotifications" style="display: none;">
                <div class="notification-banner">
                    <span class="notification-icon">ℹ️</span>
                    <span class="notification-text">Settings saved successfully</span>
                    <button class="notification-close" onclick="hideSettingsNotification()">×</button>
                </div>
            </div>

            <div class="settings-content">
                <div class="settings-section active" id="appearanceSection">
                    <h3>🎨 Appearance</h3>
                    <div class="setting-group">
                        <div class="setting-item">
                            <label for="themeSelect">Theme</label>
                            <select id="themeSelect">
                                <option value="light">☀️ Light</option>
                                <option value="dark" selected>🌙 Dark</option>
                                <option value="auto">🌓 Auto (System)</option>
                            </select>
                            <div class="setting-description">Choose your preferred color theme</div>
                        </div>

                        <div class="setting-item">
                            <label for="accentColor">Accent Color</label>
                            <div class="color-picker">
                                <input type="color" id="accentColor" value="#007bff">
                                <span class="color-preview" id="accentPreview"></span>
                            </div>
                            <div class="setting-description">Customize the accent color used throughout the interface</div>
                        </div>

                        <div class="setting-item">
                            <label for="fontSize">Font Size</label>
                            <select id="fontSize">
                                <option value="small">Small</option>
                                <option value="medium" selected>Medium</option>
                                <option value="large">Large</option>
                                <option value="xl">Extra Large</option>
                            </select>
                            <div class="setting-description">Adjust text size for better readability</div>
                        </div>

                        <div class="setting-item">
                            <label for="fontFamily">Font Family</label>
                            <select id="fontFamily">
                                <option value="inter" selected>Inter</option>
                                <option value="system">System Default</option>
                                <option value="serif">Serif</option>
                                <option value="monospace">Monospace</option>
                            </select>
                            <div class="setting-description">Choose your preferred font style</div>
                        </div>

                        <div class="setting-item">
                            <label for="language">Language</label>
                            <select id="language">
                                <option value="en" selected>English</option>
                                <option value="es">Español</option>
                                <option value="fr">Français</option>
                                <option value="de">Deutsch</option>
                                <option value="zh">中文</option>
                                <option value="ja">日本語</option>
                            </select>
                            <div class="setting-description">Select your preferred language</div>
                        </div>

                        <div class="setting-item checkbox">
                            <input type="checkbox" id="reduceMotion" checked>
                            <label for="reduceMotion">Reduce motion and animations</label>
                            <div class="setting-description">Minimize animations for better accessibility</div>
                        </div>

                        <div class="setting-item checkbox">
                            <input type="checkbox" id="highContrast">
                            <label for="highContrast">High contrast mode</label>
                            <div class="setting-description">Increase contrast for better visibility</div>
                        </div>
                    </div>
                </div>

                <div class="settings-section" id="accountSection">
                    <h3>👤 Account</h3>
                    <div class="setting-group">
                        <div class="setting-item">
                            <label>Profile Picture</label>
                            <div class="profile-picture-upload">
                                <div class="current-avatar" id="currentAvatar">
                                    <span class="avatar-placeholder">👤</span>
                                </div>
                                <div class="upload-controls">
                                    <button class="btn btn-secondary btn-sm" id="changeAvatarBtn">Change Avatar</button>
                                    <button class="btn btn-secondary btn-sm" id="removeAvatarBtn">Remove</button>
                                </div>
                            </div>
                        </div>

                        <div class="setting-item">
                            <label for="displayName">Display Name</label>
                            <input type="text" id="displayName" placeholder="Your display name">
                            <div class="setting-description">How others will see your name</div>
                        </div>

                        <div class="setting-item">
                            <label for="email">Email Address</label>
                            <input type="email" id="email" placeholder="your.email@example.com">
                            <div class="setting-description">Used for notifications and account recovery</div>
                        </div>

                        <div class="setting-item">
                            <label>Change Password</label>
                            <div class="password-change">
                                <button class="btn btn-secondary" id="changePasswordBtn">Change Password</button>
                                <div class="setting-description">Last changed 30 days ago</div>
                            </div>
                        </div>

                        <div class="setting-item">
                            <label>Two-Factor Authentication</label>
                            <div class="tfa-status">
                                <span class="status-indicator disabled">Disabled</span>
                                <button class="btn btn-primary btn-sm" id="enable2FABtn">Enable 2FA</button>
                            </div>
                            <div class="setting-description">Add an extra layer of security to your account</div>
                        </div>

                        <div class="setting-item">
                            <label>Account Status</label>
                            <div class="account-status">
                                <span class="status-badge active">Active</span>
                                <div class="account-details">
                                    <div>Member since: January 2024</div>
                                    <div>Last login: Today</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="settings-section" id="researchSection">
                    <h3>🔬 Research Settings</h3>
                    <div class="setting-group">
                        <div class="setting-item">
                            <label for="defaultModel">Default AI Model</label>
                            <select id="defaultModel">
                                <option value="llama3.2:latest" selected>Llama 3.2 (Latest)</option>
                                <option value="llama3.1:8b">Llama 3.1 8B</option>
                                <option value="llama3.1:70b">Llama 3.1 70B</option>
                                <option value="codellama">Code Llama</option>
                                <option value="mistral">Mistral</option>
                            </select>
                            <div class="setting-description">Choose your preferred AI model for research tasks</div>
                        </div>

                        <div class="setting-item">
                            <label for="temperature">Response Creativity</label>
                            <div class="slider-control">
                                <input type="range" id="temperature" min="0" max="2" step="0.1" value="0.7">
                                <span class="slider-value" id="temperatureValue">0.7</span>
                            </div>
                            <div class="setting-description">Higher values make responses more creative, lower values more focused</div>
                        </div>

                        <div class="setting-item">
                            <label for="maxTokens">Maximum Response Length</label>
                            <select id="maxTokens">
                                <option value="500">Short (500 tokens)</option>
                                <option value="1000" selected>Medium (1000 tokens)</option>
                                <option value="2000">Long (2000 tokens)</option>
                                <option value="4000">Very Long (4000 tokens)</option>
                                <option value="unlimited">Unlimited</option>
                            </select>
                            <div class="setting-description">Control how long AI responses can be</div>
                        </div>

                        <div class="setting-item">
                            <label for="defaultDepth">Default Research Depth</label>
                            <select id="defaultDepth">
                                <option value="quick">Quick Overview</option>
                                <option value="standard" selected>Standard Research</option>
                                <option value="deep">Deep Analysis</option>
                                <option value="comprehensive">Comprehensive Study</option>
                            </select>
                            <div class="setting-description">Default depth for new research sessions</div>
                        </div>

                        <div class="setting-item">
                            <label for="timeLimit">Default Time Limit</label>
                            <select id="timeLimit">
                                <option value="300">5 minutes</option>
                                <option value="900" selected>15 minutes</option>
                                <option value="1800">30 minutes</option>
                                <option value="3600">1 hour</option>
                                <option value="7200">2 hours</option>
                                <option value="unlimited">No limit</option>
                            </select>
                            <div class="setting-description">Default time limit for research sessions</div>
                        </div>

                        <div class="setting-item checkbox">
                            <input type="checkbox" id="autoSave" checked>
                            <label for="autoSave">Auto-save research sessions</label>
                            <div class="setting-description">Automatically save your research progress</div>
                        </div>

                        <div class="setting-item checkbox">
                            <input type="checkbox" id="autoExport" checked>
                            <label for="autoExport">Auto-export results</label>
                            <div class="setting-description">Automatically export research results when complete</div>
                        </div>

                        <div class="setting-item checkbox">
                            <input type="checkbox" id="saveToKnowledge" checked>
                            <label for="saveToKnowledge">Save findings to knowledge base</label>
                            <div class="setting-description">Automatically add research findings to your knowledge base</div>
                        </div>
                    </div>
                </div>

                <div class="settings-section" id="privacySection">
                    <h3>🔒 Privacy & Security</h3>
                    <div class="setting-group">
                        <div class="setting-item checkbox">
                            <input type="checkbox" id="localOnly" checked>
                            <label for="localOnly">Local processing only</label>
                            <div class="setting-description">Ensure all data processing happens locally on your device</div>
                        </div>

                        <div class="setting-item checkbox">
                            <input type="checkbox" id="encryptData" checked>
                            <label for="encryptData">Encrypt stored data</label>
                            <div class="setting-description">Encrypt sensitive data stored on your device</div>
                        </div>

                        <div class="setting-item">
                            <label for="dataRetention">Data Retention</label>
                            <select id="dataRetention">
                                <option value="forever">Forever</option>
                                <option value="1year" selected>1 Year</option>
                                <option value="6months">6 Months</option>
                                <option value="1month">1 Month</option>
                                <option value="1week">1 Week</option>
                            </select>
                            <div class="setting-description">How long to keep your research data and chat history</div>
                        </div>

                        <div class="setting-item">
                            <label>Export Your Data</label>
                            <div class="data-export">
                                <button class="btn btn-secondary" id="exportDataBtn">Export All Data</button>
                                <div class="setting-description">Download all your data in a portable format</div>
                            </div>
                        </div>

                        <div class="setting-item">
                            <label>Clear Data</label>
                            <div class="data-clear">
                                <button class="btn btn-warning btn-sm" id="clearCacheBtn">Clear Cache</button>
                                <button class="btn btn-danger btn-sm" id="clearAllDataBtn">Clear All Data</button>
                                <div class="setting-description">Remove temporary or all stored data</div>
                            </div>
                        </div>

                        <div class="setting-item">
                            <label>Privacy Mode</label>
                            <div class="privacy-mode">
                                <select id="privacyMode">
                                    <option value="standard" selected>Standard</option>
                                    <option value="high">High Privacy</option>
                                    <option value="maximum">Maximum Privacy</option>
                                </select>
                                <div class="setting-description">Adjust privacy settings for different levels of data protection</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="settings-section" id="integrationsSection">
                    <h3>🔗 Integrations</h3>
                    <div class="setting-group">
                        <div class="integration-item connected">
                            <div class="integration-info">
                                <div class="integration-name">Ollama AI Models</div>
                                <div class="integration-desc">Local AI model server for chat and research</div>
                            </div>
                            <div class="integration-status">
                                <span class="status-indicator connected">Connected</span>
                                <button class="btn btn-secondary btn-sm" onclick="configureOllama()">Configure</button>
                            </div>
                        </div>

                        <div class="integration-item">
                            <div class="integration-info">
                                <div class="integration-name">GitHub</div>
                                <div class="integration-desc">Access to code repositories and documentation</div>
                            </div>
                            <div class="integration-controls">
                                <button class="btn btn-primary btn-sm" onclick="connectGitHub()">Connect</button>
                                <div class="integration-features">
                                    <small>• Repository access<br>• Issue tracking<br>• Code search</small>
                                </div>
                            </div>
                        </div>

                        <div class="integration-item">
                            <div class="integration-info">
                                <div class="integration-name">Kiwix</div>
                                <div class="integration-desc">Offline knowledge base with Wikipedia and more</div>
                            </div>
                            <div class="integration-controls">
                                <button class="btn btn-primary btn-sm" onclick="connectKiwix()">Setup</button>
                                <div class="integration-features">
                                    <small>• Wikipedia<br>• Stack Overflow<br>• Project docs</small>
                                </div>
                            </div>
                        </div>

                        <div class="integration-item">
                            <div class="integration-info">
                                <div class="integration-name">Web Search APIs</div>
                                <div class="integration-desc">Enhanced web search capabilities</div>
                            </div>
                            <div class="integration-controls">
                                <button class="btn btn-primary btn-sm" onclick="configureWebSearch()">Configure</button>
                                <div class="integration-features">
                                    <small>• Google Custom Search<br>• Bing Web Search<br>• DuckDuckGo</small>
                                </div>
                            </div>
                        </div>

                        <div class="integration-item">
                            <div class="integration-info">
                                <div class="integration-name">Cloud Storage</div>
                                <div class="integration-desc">Backup and sync your knowledge base</div>
                            </div>
                            <div class="integration-controls">
                                <button class="btn btn-primary btn-sm" onclick="connectCloudStorage()">Connect</button>
                                <div class="integration-features">
                                    <small>• Google Drive<br>• Dropbox<br>• OneDrive</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="settings-section" id="advancedSection">
                    <h3>⚙️ Advanced Settings</h3>
                    <div class="setting-group">
                        <div class="setting-item">
                            <label for="maxMemory">Memory Limit (GB)</label>
                            <div class="slider-control">
                                <input type="range" id="maxMemory" min="1" max="16" step="0.5" value="12">
                                <span class="slider-value" id="maxMemoryValue">12GB</span>
                            </div>
                            <div class="setting-description">Maximum memory usage for AI models and processing</div>
                        </div>

                        <div class="setting-item">
                            <label for="concurrency">Concurrent Operations</label>
                            <select id="concurrency">
                                <option value="1">1 (Sequential)</option>
                                <option value="2" selected>2</option>
                                <option value="4">4</option>
                                <option value="8">8 (High Performance)</option>
                            </select>
                            <div class="setting-description">Number of simultaneous operations allowed</div>
                        </div>

                        <div class="setting-item checkbox">
                            <input type="checkbox" id="enableLogging" checked>
                            <label for="enableLogging">Enable detailed logging</label>
                            <div class="setting-description">Log detailed information for troubleshooting</div>
                        </div>

                        <div class="setting-item checkbox">
                            <input type="checkbox" id="enableAnalytics">
                            <label for="enableAnalytics">Enable usage analytics</label>
                            <div class="setting-description">Help improve the product by sharing anonymous usage data</div>
                        </div>

                        <div class="setting-item">
                            <label for="updateChannel">Update Channel</label>
                            <select id="updateChannel">
                                <option value="stable" selected>Stable</option>
                                <option value="beta">Beta</option>
                                <option value="nightly">Nightly</option>
                            </select>
                            <div class="setting-description">Choose how often to receive updates</div>
                        </div>

                        <div class="setting-item">
                            <label>Development Options</label>
                            <div class="dev-options">
                                <button class="btn btn-secondary btn-sm" id="openDevTools">Developer Tools</button>
                                <button class="btn btn-secondary btn-sm" id="resetToDefaults">Factory Reset</button>
                                <div class="setting-description">Advanced options for developers and troubleshooting</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="settings-section" id="backupsSection">
                    <h3>💾 Backups & Recovery</h3>
                    <div class="setting-group">
                        <div class="setting-item">
                            <label>Automatic Backups</label>
                            <div class="backup-settings">
                                <div class="backup-frequency">
                                    <select id="backupFrequency">
                                        <option value="daily">Daily</option>
                                        <option value="weekly" selected>Weekly</option>
                                        <option value="monthly">Monthly</option>
                                        <option value="manual">Manual Only</option>
                                    </select>
                                </div>
                                <div class="backup-status">
                                    <span class="backup-last">Last backup: Today 2:30 PM</span>
                                </div>
                            </div>
                            <div class="setting-description">Automatically backup your data and settings</div>
                        </div>

                        <div class="setting-item">
                            <label>Backup Location</label>
                            <div class="backup-location">
                                <input type="text" id="backupPath" readonly value="~/Documents/RouterPhase1/Backups">
                                <button class="btn btn-secondary btn-sm" id="changeBackupPath">Change</button>
                            </div>
                            <div class="setting-description">Where to store your backup files</div>
                        </div>

                        <div class="setting-item">
                            <label>Backup Contents</label>
                            <div class="backup-contents">
                                <div class="checkbox-group">
                                    <label><input type="checkbox" checked id="backupChats"> Chat History</label>
                                    <label><input type="checkbox" checked id="backupResearch"> Research Sessions</label>
                                    <label><input type="checkbox" checked id="backupKnowledge"> Knowledge Base</label>
                                    <label><input type="checkbox" checked id="backupSettings"> Settings</label>
                                    <label><input type="checkbox" id="backupModels"> Downloaded Models</label>
                                </div>
                            </div>
                            <div class="setting-description">Choose what to include in backups</div>
                        </div>

                        <div class="setting-item">
                            <label>Manual Backup</label>
                            <div class="manual-backup">
                                <button class="btn btn-primary" id="createBackupBtn">Create Backup Now</button>
                                <button class="btn btn-secondary" id="restoreBackupBtn">Restore from Backup</button>
                            </div>
                            <div class="setting-description">Create or restore backups manually</div>
                        </div>

                        <div class="setting-item">
                            <label>Backup History</label>
                            <div class="backup-history">
                                <div class="backup-list" id="backupList">
                                    <div class="backup-item">
                                        <div class="backup-info">
                                            <div class="backup-name">backup_2024-01-06_14-30.zip</div>
                                            <div class="backup-size">245 MB</div>
                                        </div>
                                        <div class="backup-actions">
                                            <button class="btn btn-secondary btn-sm">Download</button>
                                            <button class="btn btn-danger btn-sm">Delete</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        let currentSection = 'appearance';
        let settingsChanged = false;

        document.addEventListener('DOMContentLoaded', function() {{
            const token = localStorage.getItem('accessToken');
            if (!token) {{
                window.location.href = '/login';
                return;
            }}

            initializeSettings();
            setupEventListeners();
        }});

        function initializeSettings() {{
            loadCurrentSettings();
            setupColorPreview();
            setupSliders();
            updateSectionNavigation();
        }}

        function setupEventListeners() {{
            // Navigation
            document.querySelectorAll('.nav-item a').forEach(link => {{
                link.addEventListener('click', (e) => {{
                    e.preventDefault();
                    const section = e.target.closest('a').href.split('/').pop() || 'appearance';
                    switchSection(section);
                }});
            }});

            // Save and reset buttons
            document.getElementById('saveSettingsBtn').addEventListener('click', saveSettings);
            document.getElementById('resetSettingsBtn').addEventListener('click', resetSettings);

            // Theme and appearance
            document.getElementById('themeSelect').addEventListener('change', (e) => {{
                applyTheme(e.target.value);
                markSettingsChanged();
            }});
            document.getElementById('accentColor').addEventListener('input', (e) => {{
                updateAccentColor(e.target.value);
                markSettingsChanged();
            }});
            document.getElementById('fontSize').addEventListener('change', markSettingsChanged);
            document.getElementById('fontFamily').addEventListener('change', markSettingsChanged);
            document.getElementById('language').addEventListener('change', markSettingsChanged);

            // Research settings
            document.getElementById('defaultModel').addEventListener('change', markSettingsChanged);
            document.getElementById('temperature').addEventListener('input', updateTemperatureValue);
            document.getElementById('maxTokens').addEventListener('change', markSettingsChanged);
            document.getElementById('defaultDepth').addEventListener('change', markSettingsChanged);
            document.getElementById('timeLimit').addEventListener('change', markSettingsChanged);

            // Checkboxes
            document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {{
                checkbox.addEventListener('change', markSettingsChanged);
            }});

            // Selects
            document.querySelectorAll('select').forEach(select => {{
                select.addEventListener('change', markSettingsChanged);
            }});

            // Account actions
            document.getElementById('changeAvatarBtn').addEventListener('click', changeAvatar);
            document.getElementById('removeAvatarBtn').addEventListener('click', removeAvatar);
            document.getElementById('changePasswordBtn').addEventListener('click', changePassword);
            document.getElementById('enable2FABtn').addEventListener('click', enable2FA);

            // Privacy actions
            document.getElementById('exportDataBtn').addEventListener('click', exportData);
            document.getElementById('clearCacheBtn').addEventListener('click', clearCache);
            document.getElementById('clearAllDataBtn').addEventListener('click', clearAllData);

            // Integration actions
            document.querySelectorAll('.integration-item button').forEach(btn => {{
                btn.addEventListener('click', handleIntegrationAction);
            }});

            // Advanced actions
            document.getElementById('openDevTools').addEventListener('click', openDevTools);
            document.getElementById('resetToDefaults').addEventListener('click', resetToDefaults);

            // Backup actions
            document.getElementById('createBackupBtn').addEventListener('click', createBackup);
            document.getElementById('restoreBackupBtn').addEventListener('click', restoreBackup);
            document.getElementById('changeBackupPath').addEventListener('click', changeBackupPath);
        }}

        function switchSection(section) {{
            currentSection = section;

            // Update navigation
            document.querySelectorAll('.nav-item').forEach(item => {{
                item.classList.remove('active');
            }});

            const activeLink = document.querySelector(`a[href*="${{section}}"]`);
            if (activeLink) {{
                activeLink.closest('.nav-item').classList.add('active');
            }}

            // Update content
            document.querySelectorAll('.settings-section').forEach(sec => {{
                sec.classList.remove('active');
            }});

            const sectionId = section + 'Section';
            const targetSection = document.getElementById(sectionId);
            if (targetSection) {{
                targetSection.classList.add('active');
            }}

            // Update URL without reload
            history.pushState(null, null, `/settings${{section !== 'appearance' ? '/' + section : ''}}`);
        }}

        function updateSectionNavigation() {{
            // Highlight current section based on URL
            const path = window.location.pathname;
            const section = path.split('/').pop() || 'appearance';
            switchSection(section);
        }}

        async function loadCurrentSettings() {{
            const token = localStorage.getItem('accessToken');
            try {{
                const response = await fetch('/api/config', {{
                    headers: {{ 'Authorization': `Bearer ${{token}}` }}
                }});

                if (response.ok) {{
                    const settings = await response.json();
                    applySettingsToForm(settings);
                }}
            }} catch (error) {{
                console.error('Failed to load settings:', error);
            }}
        }}

        function applySettingsToForm(settings) {{
            // Apply loaded settings to form fields
            Object.keys(settings).forEach(key => {{
                const element = document.getElementById(key);
                if (element) {{
                    if (element.type === 'checkbox') {{
                        element.checked = settings[key];
                    }} else {{
                        element.value = settings[key];
                    }}
                }}
            }});

            // Update UI elements
            updateAccentColor(document.getElementById('accentColor').value);
            updateTemperatureValue();
            updateMaxMemoryValue();
        }}

        function setupColorPreview() {{
            const accentColor = document.getElementById('accentColor');
            const preview = document.getElementById('accentPreview');

            function updatePreview() {{
                preview.style.backgroundColor = accentColor.value;
            }}

            accentColor.addEventListener('input', updatePreview);
            updatePreview();
        }}

        function setupSliders() {{
            const temperature = document.getElementById('temperature');
            const maxMemory = document.getElementById('maxMemory');

            temperature.addEventListener('input', updateTemperatureValue);
            maxMemory.addEventListener('input', updateMaxMemoryValue);

            updateTemperatureValue();
            updateMaxMemoryValue();
        }}

        function updateTemperatureValue() {{
            const temperature = document.getElementById('temperature');
            const value = document.getElementById('temperatureValue');
            value.textContent = temperature.value;
        }}

        function updateMaxMemoryValue() {{
            const maxMemory = document.getElementById('maxMemory');
            const value = document.getElementById('maxMemoryValue');
            value.textContent = maxMemory.value + 'GB';
        }}

        function updateAccentColor(color) {{
            document.documentElement.style.setProperty('--accent-color', color);
            const preview = document.getElementById('accentPreview');
            if (preview) {{
                preview.style.backgroundColor = color;
            }}
        }}

        function applyTheme(theme) {{
            document.documentElement.setAttribute('data-theme', theme);
        }}

        function markSettingsChanged() {{
            settingsChanged = true;
            document.getElementById('saveSettingsBtn').classList.add('unsaved');
        }}

        async function saveSettings() {{
            const token = localStorage.getItem('accessToken');

            const settings = {{
                // Appearance
                theme: document.getElementById('themeSelect').value,
                accentColor: document.getElementById('accentColor').value,
                fontSize: document.getElementById('fontSize').value,
                fontFamily: document.getElementById('fontFamily').value,
                language: document.getElementById('language').value,
                reduceMotion: document.getElementById('reduceMotion').checked,
                highContrast: document.getElementById('highContrast').checked,

                // Research
                defaultModel: document.getElementById('defaultModel').value,
                temperature: parseFloat(document.getElementById('temperature').value),
                maxTokens: document.getElementById('maxTokens').value,
                defaultDepth: document.getElementById('defaultDepth').value,
                timeLimit: document.getElementById('timeLimit').value,
                autoSave: document.getElementById('autoSave').checked,
                autoExport: document.getElementById('autoExport').checked,
                saveToKnowledge: document.getElementById('saveToKnowledge').checked,

                // Privacy
                localOnly: document.getElementById('localOnly').checked,
                encryptData: document.getElementById('encryptData').checked,
                dataRetention: document.getElementById('dataRetention').value,
                privacyMode: document.getElementById('privacyMode').value,

                // Advanced
                maxMemory: parseFloat(document.getElementById('maxMemory').value),
                concurrency: parseInt(document.getElementById('concurrency').value),
                enableLogging: document.getElementById('enableLogging').checked,
                enableAnalytics: document.getElementById('enableAnalytics').checked,
                updateChannel: document.getElementById('updateChannel').value
            }};

            try {{
                const response = await fetch('/api/config', {{
                    method: 'POST',
                    headers: {{
                        'Authorization': `Bearer ${{token}}`,
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify(settings)
                }});

                if (response.ok) {{
                    settingsChanged = false;
                    document.getElementById('saveSettingsBtn').classList.remove('unsaved');
                    showSettingsNotification('Settings saved successfully!', 'success');
                }} else {{
                    showSettingsNotification('Failed to save settings', 'error');
                }}
            }} catch (error) {{
                showSettingsNotification('Error saving settings: ' + error.message, 'error');
            }}
        }}

        function resetSettings() {{
            if (confirm('Are you sure you want to reset all settings to defaults? This will not save automatically.')) {{
                // Reset appearance
                document.getElementById('themeSelect').value = 'dark';
                document.getElementById('accentColor').value = '#007bff';
                document.getElementById('fontSize').value = 'medium';
                document.getElementById('fontFamily').value = 'inter';
                document.getElementById('language').value = 'en';
                document.getElementById('reduceMotion').checked = false;
                document.getElementById('highContrast').checked = false;

                // Reset research
                document.getElementById('defaultModel').value = 'llama3.2:latest';
                document.getElementById('temperature').value = '0.7';
                document.getElementById('maxTokens').value = '1000';
                document.getElementById('defaultDepth').value = 'standard';
                document.getElementById('timeLimit').value = '1800';
                document.getElementById('autoSave').checked = true;
                document.getElementById('autoExport').checked = true;
                document.getElementById('saveToKnowledge').checked = true;

                // Reset privacy
                document.getElementById('localOnly').checked = true;
                document.getElementById('encryptData').checked = true;
                document.getElementById('dataRetention').value = '1year';
                document.getElementById('privacyMode').value = 'standard';

                // Reset advanced
                document.getElementById('maxMemory').value = '12';
                document.getElementById('concurrency').value = '2';
                document.getElementById('enableLogging').checked = true;
                document.getElementById('enableAnalytics').checked = false;
                document.getElementById('updateChannel').value = 'stable';

                applyTheme('dark');
                updateAccentColor('#007bff');
                updateTemperatureValue();
                updateMaxMemoryValue();
                markSettingsChanged();
            }}
        }}

        function showSettingsNotification(message, type = 'info') {{
            const notification = document.getElementById('settingsNotifications');
            const banner = notification.querySelector('.notification-banner');
            const text = banner.querySelector('.notification-text');

            banner.className = `notification-banner ${{type}}`;
            text.textContent = message;

            notification.style.display = 'block';

            setTimeout(() => {{
                hideSettingsNotification();
            }}, 5000);
        }}

        function hideSettingsNotification() {{
            document.getElementById('settingsNotifications').style.display = 'none';
        }}

        // Placeholder functions for account actions
        function changeAvatar() {{ UI.showToast('Avatar change coming soon!', 'info'); }}
        function removeAvatar() {{ UI.showToast('Avatar removal coming soon!', 'info'); }}
        function changePassword() {{ UI.showToast('Password change coming soon!', 'info'); }}
        function enable2FA() {{ UI.showToast('2FA setup coming soon!', 'info'); }}

        // Placeholder functions for privacy actions
        function exportData() {{ UI.showToast('Data export coming soon!', 'info'); }}
        function clearCache() {{ UI.showToast('Cache clearing coming soon!', 'info'); }}
        function clearAllData() {{ UI.showToast('Data clearing coming soon!', 'info'); }}

        // Placeholder functions for integrations
        function configureOllama() {{ UI.showToast('Ollama configuration coming soon!', 'info'); }}
        function connectGitHub() {{ UI.showToast('GitHub integration coming soon!', 'info'); }}
        function connectKiwix() {{ UI.showToast('Kiwix setup coming soon!', 'info'); }}
        function configureWebSearch() {{ UI.showToast('Web search configuration coming soon!', 'info'); }}
        function connectCloudStorage() {{ UI.showToast('Cloud storage integration coming soon!', 'info'); }}

        // Placeholder functions for advanced
        function openDevTools() {{ UI.showToast('Developer tools coming soon!', 'info'); }}
        function resetToDefaults() {{ UI.showToast('Factory reset coming soon!', 'info'); }}

        // Placeholder functions for backups
        function createBackup() {{ UI.showToast('Backup creation coming soon!', 'info'); }}
        function restoreBackup() {{ UI.showToast('Backup restoration coming soon!', 'info'); }}
        function changeBackupPath() {{ UI.showToast('Backup path change coming soon!', 'info'); }}

        function handleIntegrationAction(e) {{
            const action = e.target.textContent.toLowerCase().replace(' ', '');
            switch (action) {{
                case 'configure': configureOllama(); break;
                case 'connect': connectGitHub(); break;
                case 'setup': connectKiwix(); break;
                default: UI.showToast('Integration action coming soon!', 'info');
            }}
        }}
    </script>
</body>
</html>"""

def modern_profile_page():
    """User profile page with activity and customization"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Profile - Router Phase 1</title>
    <link rel="stylesheet" href="/static/css/modern.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="profile-page">
    <div class="app-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>Profile</h2>
            </div>
            <ul class="sidebar-nav">
                <li class="nav-item active">
                    <a href="/profile">
                        <span class="nav-icon">👤</span>
                        Overview
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/profile/activity">
                        <span class="nav-icon">📊</span>
                        Activity
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/profile/achievements">
                        <span class="nav-icon">🏆</span>
                        Achievements
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/profile/preferences">
                        <span class="nav-icon">⚙️</span>
                        Preferences
                    </a>
                </li>
            </ul>
        </nav>

        <main class="main-content">
            <header class="page-header">
                <h1>My Profile</h1>
                <div class="header-actions">
                    <button class="btn btn-secondary" id="editProfileBtn">
                        <span class="btn-icon">✏️</span>
                        Edit Profile
                    </button>
                </div>
            </header>

            <div class="profile-content">
                <div class="profile-header">
                    <div class="profile-avatar">
                        <div class="avatar-placeholder" id="profileAvatar">
                            👤
                        </div>
                        <button class="avatar-edit-btn" id="changeAvatarBtn">📷</button>
                    </div>
                    <div class="profile-info">
                        <h2 id="profileName">Loading...</h2>
                        <p id="profileEmail">user@example.com</p>
                        <div class="profile-meta">
                            <span class="meta-item">Member since <span id="memberSince">Unknown</span></span>
                            <span class="meta-item">Last active <span id="lastActive">Recently</span></span>
                        </div>
                    </div>
                </div>

                <div class="profile-stats">
                    <div class="stat-card">
                        <div class="stat-value" id="totalChats">0</div>
                        <div class="stat-label">Total Chats</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="totalResearch">0</div>
                        <div class="stat-label">Research Sessions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="knowledgeItems">0</div>
                        <div class="stat-label">Knowledge Items</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="achievements">0</div>
                        <div class="stat-label">Achievements</div>
                    </div>
                </div>

                <div class="profile-section">
                    <h3>Recent Activity</h3>
                    <div class="activity-feed" id="recentActivity">
                        <div class="activity-item loading">
                            <div class="activity-icon">⏳</div>
                            <div class="activity-content">
                                <div class="activity-title">Loading activity...</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="profile-section">
                    <h3>Research Interests</h3>
                    <div class="interests-grid" id="researchInterests">
                        <div class="interest-tag">AI & Machine Learning</div>
                        <div class="interest-tag">Data Science</div>
                        <div class="interest-tag">Software Engineering</div>
                        <div class="interest-tag">Research Methodology</div>
                        <button class="btn btn-secondary btn-sm" id="editInterestsBtn">Edit Interests</button>
                    </div>
                </div>

                <div class="profile-section">
                    <h3>Account Settings</h3>
                    <div class="account-settings">
                        <div class="setting-row">
                            <div class="setting-info">
                                <div class="setting-name">Password</div>
                                <div class="setting-desc">Last changed 30 days ago</div>
                            </div>
                            <button class="btn btn-secondary btn-sm" id="changePasswordBtn">Change</button>
                        </div>
                        <div class="setting-row">
                            <div class="setting-info">
                                <div class="setting-name">Two-Factor Authentication</div>
                                <div class="setting-desc">Add an extra layer of security</div>
                            </div>
                            <button class="btn btn-primary btn-sm" id="enable2FABtn">Enable</button>
                        </div>
                        <div class="setting-row">
                            <div class="setting-info">
                                <div class="setting-name">Data Export</div>
                                <div class="setting-desc">Download all your data</div>
                            </div>
                            <button class="btn btn-secondary btn-sm" id="exportDataBtn">Export</button>
                        </div>
                        <div class="setting-row danger">
                            <div class="setting-info">
                                <div class="setting-name">Delete Account</div>
                                <div class="setting-desc">Permanently delete your account and all data</div>
                            </div>
                            <button class="btn btn-danger btn-sm" id="deleteAccountBtn">Delete</button>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const token = localStorage.getItem('accessToken');
            if (!token) {{
                window.location.href = '/login';
                return;
            }}

            initializeProfile();
            setupEventListeners();
        }});

        function initializeProfile() {{
            loadProfileData();
        }}

        function setupEventListeners() {{
            document.getElementById('editProfileBtn').addEventListener('click', editProfile);
            document.getElementById('changeAvatarBtn').addEventListener('click', changeAvatar);
            document.getElementById('editInterestsBtn').addEventListener('click', editInterests);
            document.getElementById('changePasswordBtn').addEventListener('click', changePassword);
            document.getElementById('enable2FABtn').addEventListener('click', enable2FA);
            document.getElementById('exportDataBtn').addEventListener('click', exportData);
            document.getElementById('deleteAccountBtn').addEventListener('click', deleteAccount);
        }}

        async function loadProfileData() {{
            const token = localStorage.getItem('accessToken');
            try {{
                // Load user info
                const userResponse = await fetch('/api/auth/me', {{
                    headers: {{ 'Authorization': `Bearer ${{token}}` }}
                }});

                if (userResponse.ok) {{
                    const user = await userResponse.json();
                    document.getElementById('profileName').textContent = user.username;
                    document.getElementById('profileEmail').textContent = user.username + '@example.com'; // Placeholder
                    document.getElementById('memberSince').textContent = 'January 2024'; // Placeholder
                    document.getElementById('lastActive').textContent = 'Today'; // Placeholder
                }}

                // Load stats
                const statsResponse = await fetch('/api/profile/stats', {{
                    headers: {{ 'Authorization': `Bearer ${{token}}` }}
                }});

                if (statsResponse.ok) {{
                    const stats = await statsResponse.json();
                    updateStats(stats);
                }} else {{
                    // Fallback stats
                    updateStats({{
                        chats: 0,
                        research: 0,
                        knowledge: 0,
                        achievements: 0
                    }});
                }}

                // Load recent activity
                const activityResponse = await fetch('/api/profile/activity', {{
                    headers: {{ 'Authorization': `Bearer ${{token}}` }}
                }});

                if (activityResponse.ok) {{
                    const activities = await activityResponse.json();
                    updateActivity(activities);
                }} else {{
                    // Placeholder activity
                    updateActivity([
                        {{
                            type: 'chat',
                            title: 'Started new conversation',
                            timestamp: new Date().toISOString()
                        }},
                        {{
                            type: 'research',
                            title: 'Completed research session',
                            timestamp: new Date(Date.now() - 3600000).toISOString()
                        }}
                    ]);
                }}

            }} catch (error) {{
                console.error('Failed to load profile data:', error);
            }}
        }}

        function updateStats(stats) {{
            document.getElementById('totalChats').textContent = stats.chats || 0;
            document.getElementById('totalResearch').textContent = stats.research || 0;
            document.getElementById('knowledgeItems').textContent = stats.knowledge || 0;
            document.getElementById('achievements').textContent = stats.achievements || 0;
        }}

        function updateActivity(activities) {{
            const container = document.getElementById('recentActivity');
            container.innerHTML = '';

            if (activities.length === 0) {{
                container.innerHTML = '<div class="no-activity">No recent activity</div>';
                return;
            }}

            activities.forEach(activity => {{
                const item = document.createElement('div');
                item.className = 'activity-item';
                item.innerHTML = `
                    <div class="activity-icon">${{getActivityIcon(activity.type)}}</div>
                    <div class="activity-content">
                        <div class="activity-title">${{activity.title}}</div>
                        <div class="activity-time">${{formatRelativeTime(activity.timestamp)}}</div>
                    </div>
                `;
                container.appendChild(item);
            }});
        }}

        function getActivityIcon(type) {{
            const icons = {{
                'chat': '💬',
                'research': '🔬',
                'knowledge': '📚',
                'achievement': '🏆'
            }};
            return icons[type] || '📝';
        }}

        // Placeholder functions
        function editProfile() {{ UI.showToast('Edit profile functionality coming soon!', 'info'); }}
        function changeAvatar() {{ UI.showToast('Avatar change functionality coming soon!', 'info'); }}
        function editInterests() {{ UI.showToast('Edit interests functionality coming soon!', 'info'); }}
        function changePassword() {{ UI.showToast('Password change functionality coming soon!', 'info'); }}
        function enable2FA() {{ UI.showToast('2FA setup functionality coming soon!', 'info'); }}
        function exportData() {{ UI.showToast('Data export functionality coming soon!', 'info'); }}
        function deleteAccount() {{ UI.showToast('Account deletion requires confirmation and comes with warnings!', 'warning'); }}
    </script>
</body>
</html>"""

def modern_help_page():
    """Comprehensive help system with tutorials"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Help & Documentation - Router Phase 1</title>
    <link rel="stylesheet" href="/static/css/modern.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="help-page">
    <div class="app-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>Help Center</h2>
            </div>
            <ul class="sidebar-nav">
                <li class="nav-item active">
                    <a href="/help">
                        <span class="nav-icon">❓</span>
                        Getting Started
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/help/chat">
                        <span class="nav-icon">💬</span>
                        Using Chat
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/help/research">
                        <span class="nav-icon">🔬</span>
                        Research Features
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/help/knowledge">
                        <span class="nav-icon">📚</span>
                        Knowledge Base
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/help/api">
                        <span class="nav-icon">🔧</span>
                        API Reference
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/help/troubleshooting">
                        <span class="nav-icon">🔧</span>
                        Troubleshooting
                    </a>
                </li>
            </ul>
        </nav>

        <main class="main-content">
            <header class="page-header">
                <h1>Help & Documentation</h1>
                <div class="header-actions">
                    <input type="text" id="helpSearch" placeholder="Search help..." class="search-input">
                </div>
            </header>

            <div class="help-content">
                <div class="help-welcome">
                    <h2>Welcome to Router Phase 1 Help</h2>
                    <p>Find answers to your questions and learn how to make the most of our AI research assistant.</p>
                </div>

                <div class="help-quick-start">
                    <h3>🚀 Quick Start Guide</h3>
                    <div class="quick-start-steps">
                        <div class="step">
                            <div class="step-number">1</div>
                            <div class="step-content">
                                <h4>Create Your Account</h4>
                                <p>Sign up for a free account to get started with Router Phase 1.</p>
                            </div>
                        </div>
                        <div class="step">
                            <div class="step-number">2</div>
                            <div class="step-content">
                                <h4>Start Your First Chat</h4>
                                <p>Begin a conversation with our AI assistant to explore capabilities.</p>
                            </div>
                        </div>
                        <div class="step">
                            <div class="step-number">3</div>
                            <div class="step-content">
                                <h4>Try Research Mode</h4>
                                <p>Experience multi-agent research with comprehensive analysis.</p>
                            </div>
                        </div>
                        <div class="step">
                            <div class="step-number">4</div>
                            <div class="step-content">
                                <h4>Build Knowledge</h4>
                                <p>Add your findings to the knowledge base for future reference.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="help-categories">
                    <div class="help-category">
                        <div class="category-icon">💬</div>
                        <h3>Chat Features</h3>
                        <p>Learn how to have effective conversations with AI assistants.</p>
                        <ul>
                            <li>Message formatting and markdown</li>
                            <li>Managing conversation history</li>
                            <li>Using different AI models</li>
                            <li>Sharing and exporting chats</li>
                        </ul>
                        <a href="/help/chat" class="btn btn-secondary">Learn More</a>
                    </div>

                    <div class="help-category">
                        <div class="category-icon">🔬</div>
                        <h3>Research Tools</h3>
                        <p>Master the advanced research capabilities.</p>
                        <ul>
                            <li>Multi-agent research orchestration</li>
                            <li>Progress tracking and monitoring</li>
                            <li>Result synthesis and analysis</li>
                            <li>Research templates and workflows</li>
                        </ul>
                        <a href="/help/research" class="btn btn-secondary">Learn More</a>
                    </div>

                    <div class="help-category">
                        <div class="category-icon">📚</div>
                        <h3>Knowledge Management</h3>
                        <p>Organize and leverage your research findings.</p>
                        <ul>
                            <li>Adding content to knowledge base</li>
                            <li>Advanced search and filtering</li>
                            <li>Knowledge graphs and relationships</li>
                            <li>Import/export functionality</li>
                        </ul>
                        <a href="/help/knowledge" class="btn btn-secondary">Learn More</a>
                    </div>

                    <div class="help-category">
                        <div class="category-icon">⚙️</div>
                        <h3>Customization</h3>
                        <p>Personalize your Router Phase 1 experience.</p>
                        <ul>
                            <li>Theme and appearance settings</li>
                            <li>Research preferences</li>
                            <li>Privacy and security options</li>
                            <li>Integration setup</li>
                        </ul>
                        <a href="/settings" class="btn btn-secondary">Go to Settings</a>
                    </div>
                </div>

                <div class="help-resources">
                    <h3>📚 Additional Resources</h3>
                    <div class="resource-grid">
                        <div class="resource-item">
                            <h4>🎥 Video Tutorials</h4>
                            <p>Step-by-step video guides for key features.</p>
                            <a href="#" class="btn btn-secondary btn-sm">Watch Videos</a>
                        </div>
                        <div class="resource-item">
                            <h4>📖 User Guide</h4>
                            <p>Comprehensive written documentation.</p>
                            <a href="#" class="btn btn-secondary btn-sm">Read Guide</a>
                        </div>
                        <div class="resource-item">
                            <h4>💬 Community Forum</h4>
                            <p>Get help from other users and share tips.</p>
                            <a href="#" class="btn btn-secondary btn-sm">Join Community</a>
                        </div>
                        <div class="resource-item">
                            <h4>🔧 API Reference</h4>
                            <p>Technical documentation for developers.</p>
                            <a href="/help/api" class="btn btn-secondary btn-sm">View API Docs</a>
                        </div>
                    </div>
                </div>

                <div class="help-contact">
                    <h3>🆘 Need More Help?</h3>
                    <p>Can't find what you're looking for? Our support team is here to help.</p>
                    <div class="contact-options">
                        <button class="btn btn-primary" onclick="contactSupport()">Contact Support</button>
                        <button class="btn btn-secondary" onclick="reportBug()">Report Bug</button>
                        <button class="btn btn-secondary" onclick="requestFeature()">Request Feature</button>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- Interactive Tutorial Modal -->
    <div class="modal" id="tutorialModal" style="display: none;">
        <div class="modal-content modal-lg">
            <div class="modal-header">
                <h3 id="tutorialTitle">Interactive Tutorial</h3>
                <button class="modal-close" onclick="closeTutorial()">×</button>
            </div>
            <div class="modal-body">
                <div class="tutorial-content" id="tutorialContent">
                    <!-- Tutorial content will be loaded here -->
                </div>
                <div class="tutorial-navigation">
                    <button class="btn btn-secondary" id="prevStepBtn" disabled>Previous</button>
                    <span id="tutorialProgress">Step 1 of 5</span>
                    <button class="btn btn-primary" id="nextStepBtn">Next</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            setupHelpSearch();
            setupTutorialSystem();
        }});

        function setupHelpSearch() {{
            const searchInput = document.getElementById('helpSearch');
            searchInput.addEventListener('input', function(e) {{
                const query = e.target.value.toLowerCase();
                // Implement search functionality
                highlightSearchResults(query);
            }});
        }}

        function highlightSearchResults(query) {{
            if (!query) {{
                // Clear highlights
                return;
            }}

            // Simple text highlighting (could be enhanced with proper search)
            const content = document.querySelector('.help-content');
            const text = content.textContent;
            const regex = new RegExp(`(${query})`, 'gi');
            const highlighted = text.replace(regex, '<mark>$1</mark>');

            // This is a simplified version - real implementation would be more sophisticated
            console.log('Search query:', query);
        }}

        function setupTutorialSystem() {{
            // Placeholder for interactive tutorial system
            window.startTutorial = function(tutorialId) {{
                document.getElementById('tutorialModal').style.display = 'flex';
                loadTutorial(tutorialId);
            }};
        }}

        function loadTutorial(tutorialId) {{
            const tutorials = {{
                'getting-started': {{
                    title: 'Getting Started with Router Phase 1',
                    steps: [
                        {{
                            title: 'Welcome',
                            content: 'Welcome to Router Phase 1! This tutorial will help you get started with our AI research assistant.'
                        }},
                        {{
                            title: 'Creating Your Account',
                            content: 'First, create your account by clicking the "Register" button on the login page.'
                        }},
                        {{
                            title: 'Your First Chat',
                            content: 'Start by creating a new chat and asking the AI assistant a question.'
                        }},
                        {{
                            title: 'Exploring Features',
                            content: 'Take a look at the sidebar to explore Research, Knowledge, and Settings.'
                        }},
                        {{
                            title: 'Next Steps',
                            content: 'You\\'re all set! Continue exploring and learning about the features.'
                        }}
                    ]
                }}
            }};

            const tutorial = tutorials[tutorialId];
            if (!tutorial) return;

            let currentStep = 0;
            const content = document.getElementById('tutorialContent');
            const title = document.getElementById('tutorialTitle');
            const progress = document.getElementById('tutorialProgress');
            const prevBtn = document.getElementById('prevStepBtn');
            const nextBtn = document.getElementById('nextStepBtn');

            title.textContent = tutorial.title;

            function showStep(stepIndex) {{
                const step = tutorial.steps[stepIndex];
                content.innerHTML = `
                    <h4>${{step.title}}</h4>
                    <p>${{step.content}}</p>
                `;
                progress.textContent = `Step ${{stepIndex + 1}} of ${{tutorial.steps.length}}`;
                prevBtn.disabled = stepIndex === 0;
                nextBtn.textContent = stepIndex === tutorial.steps.length - 1 ? 'Finish' : 'Next';
            }}

            prevBtn.addEventListener('click', function() {{
                if (currentStep > 0) {{
                    currentStep--;
                    showStep(currentStep);
                }}
            }});

            nextBtn.addEventListener('click', function() {{
                if (currentStep < tutorial.steps.length - 1) {{
                    currentStep++;
                    showStep(currentStep);
                }} else {{
                    closeTutorial();
                }}
            }});

            showStep(0);
        }}

        function closeTutorial() {{
            document.getElementById('tutorialModal').style.display = 'none';
        }}

        // Placeholder functions
        function contactSupport() {{ UI.showToast('Support contact functionality coming soon!', 'info'); }}
        function reportBug() {{ UI.showToast('Bug reporting functionality coming soon!', 'info'); }}
        function requestFeature() {{ UI.showToast('Feature request functionality coming soon!', 'info'); }}
    </script>
</body>
</html>"""

def modern_search_page():
    """Global search interface with advanced filters"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Global Search - Router Phase 1</title>
    <link rel="stylesheet" href="/static/css/modern.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="search-page">
    <div class="app-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>Search</h2>
            </div>
            <div class="search-filters-sidebar">
                <div class="filter-section">
                    <h4>Content Types</h4>
                    <label class="checkbox-label">
                        <input type="checkbox" id="searchChats" checked> Chats
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="searchResearch" checked> Research
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="searchKnowledge" checked> Knowledge
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="searchFiles"> Files
                    </label>
                </div>

                <div class="filter-section">
                    <h4>Date Range</h4>
                    <select id="dateRange">
                        <option value="all">All Time</option>
                        <option value="today">Today</option>
                        <option value="week">This Week</option>
                        <option value="month">This Month</option>
                        <option value="year">This Year</option>
                        <option value="custom">Custom Range</option>
                    </select>
                    <div id="customDateRange" style="display: none; margin-top: 10px;">
                        <input type="date" id="startDate" style="width: 100%; margin-bottom: 5px;">
                        <input type="date" id="endDate" style="width: 100%;">
                    </div>
                </div>

                <div class="filter-section">
                    <h4>Sort By</h4>
                    <select id="sortOrder">
                        <option value="relevance">Relevance</option>
                        <option value="date">Date</option>
                        <option value="title">Title</option>
                        <option value="type">Content Type</option>
                    </select>
                </div>

                <div class="filter-section">
                    <h4>Advanced Options</h4>
                    <label class="checkbox-label">
                        <input type="checkbox" id="exactMatch"> Exact phrase match
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="caseSensitive"> Case sensitive
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="includeArchived"> Include archived
                    </label>
                </div>
            </div>
        </nav>

        <main class="main-content">
            <header class="page-header">
                <h1>Global Search</h1>
                <div class="search-header-actions">
                    <button class="btn btn-secondary" id="clearSearchBtn">Clear</button>
                    <button class="btn btn-primary" id="advancedFiltersBtn">Filters</button>
                </div>
            </header>

            <div class="search-container">
                <div class="search-input-wrapper">
                    <input
                        type="text"
                        id="globalSearchInput"
                        placeholder="Search across all your content..."
                        class="search-input-large"
                        autofocus
                    >
                    <button class="btn btn-primary search-btn" id="searchBtn">
                        <span class="search-icon">🔍</span>
                        Search
                    </button>
                </div>

                <div class="search-suggestions" id="searchSuggestions" style="display: none;">
                    <div class="suggestion-item" onclick="applySuggestion('research papers')">
                        <span class="suggestion-text">research papers</span>
                        <span class="suggestion-type">Popular</span>
                    </div>
                    <div class="suggestion-item" onclick="applySuggestion('machine learning')">
                        <span class="suggestion-text">machine learning</span>
                        <span class="suggestion-type">Topic</span>
                    </div>
                    <div class="suggestion-item" onclick="applySuggestion('project status')">
                        <span class="suggestion-text">project status</span>
                        <span class="suggestion-type">Recent</span>
                    </div>
                </div>
            </div>

            <div class="search-results" id="searchResults" style="display: none;">
                <div class="results-header">
                    <div class="results-info">
                        <span id="resultsCount">0</span> results for "<span id="searchQuery"></span>"
                        <span id="searchTime"></span>
                    </div>
                    <div class="results-actions">
                        <button class="btn btn-secondary btn-sm" id="exportResultsBtn">Export</button>
                        <button class="btn btn-secondary btn-sm" id="saveSearchBtn">Save Search</button>
                    </div>
                </div>

                <div class="results-filters">
                    <div class="filter-pills">
                        <span class="filter-pill active" data-filter="all">All Results</span>
                        <span class="filter-pill" data-filter="chats">Chats</span>
                        <span class="filter-pill" data-filter="research">Research</span>
                        <span class="filter-pill" data-filter="knowledge">Knowledge</span>
                    </div>
                </div>

                <div class="results-list" id="resultsList">
                    <!-- Search results will be populated here -->
                </div>

                <div class="results-pagination" id="resultsPagination" style="display: none;">
                    <button class="btn btn-secondary btn-sm" id="prevPageBtn" disabled>Previous</button>
                    <span class="page-info">
                        Page <span id="currentPage">1</span> of <span id="totalPages">1</span>
                    </span>
                    <button class="btn btn-secondary btn-sm" id="nextPageBtn">Next</button>
                </div>
            </div>

            <div class="search-empty" id="searchEmpty">
                <div class="empty-search">
                    <div class="empty-icon">🔍</div>
                    <h3>Start searching</h3>
                    <p>Enter a search term to find content across your chats, research sessions, and knowledge base.</p>
                    <div class="search-tips">
                        <h4>Search Tips:</h4>
                        <ul>
                            <li>Use quotes for exact phrases: "machine learning"</li>
                            <li>Search by content type: type:chat or type:research</li>
                            <li>Find recent content: date:today or date:week</li>
                            <li>Combine terms: AI AND research OR papers</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="search-loading" id="searchLoading" style="display: none;">
                <div class="loading-spinner"></div>
                <p>Searching across your content...</p>
            </div>
        </main>
    </div>

    <script>
        let currentSearchQuery = '';
        let currentFilters = {};
        let searchResults = [];
        let currentPage = 1;
        const resultsPerPage = 20;

        document.addEventListener('DOMContentLoaded', function() {{
            const token = localStorage.getItem('accessToken');
            if (!token) {{
                window.location.href = '/login';
                return;
            }}

            initializeSearch();
            setupEventListeners();
        }});

        function initializeSearch() {{
            const urlParams = new URLSearchParams(window.location.search);
            const query = urlParams.get('q');
            if (query) {{
                document.getElementById('globalSearchInput').value = query;
                performSearch(query);
            }
        }}

        function setupEventListeners() {{
            const searchInput = document.getElementById('globalSearchInput');
            searchInput.addEventListener('input', handleSearchInput);
            searchInput.addEventListener('keydown', handleSearchKeydown);

            document.getElementById('searchBtn').addEventListener('click', () => performSearch());
            document.getElementById('clearSearchBtn').addEventListener('click', clearSearch);
            document.getElementById('advancedFiltersBtn').addEventListener('click', toggleSidebar);
            document.getElementById('exportResultsBtn').addEventListener('click', exportResults);
            document.getElementById('saveSearchBtn').addEventListener('click', saveSearch);

            // Filter checkboxes
            document.querySelectorAll('.checkbox-label input').forEach(checkbox => {{
                checkbox.addEventListener('change', updateFilters);
            }});

            // Filter selects
            document.getElementById('dateRange').addEventListener('change', handleDateRangeChange);
            document.getElementById('sortOrder').addEventListener('change', updateFilters);

            // Filter pills
            document.querySelectorAll('.filter-pill').forEach(pill => {{
                pill.addEventListener('click', (e) => filterByType(e.target.dataset.filter));
            }});

            // Pagination
            document.getElementById('prevPageBtn').addEventListener('click', () => changePage(-1));
            document.getElementById('nextPageBtn').addEventListener('click', () => changePage(1));
        }}

        function handleSearchInput(e) {{
            const query = e.target.value.trim();
            if (query.length > 2) {{
                showSuggestions(query);
            }} else {{
                hideSuggestions();
            }
        }}

        function handleSearchKeydown(e) {{
            if (e.key === 'Enter') {{
                performSearch();
            }} else if (e.key === 'Escape') {{
                hideSuggestions();
            }}
        }}

        function showSuggestions(query) {{
            // Simple suggestion logic - in real implementation, this would call an API
            const suggestions = document.getElementById('searchSuggestions');
            suggestions.style.display = 'block';

            // Filter suggestions based on query
            const suggestionItems = suggestions.querySelectorAll('.suggestion-item');
            suggestionItems.forEach(item => {{
                const text = item.querySelector('.suggestion-text').textContent.toLowerCase();
                item.style.display = text.includes(query.toLowerCase()) ? 'flex' : 'none';
            });
        }}

        function hideSuggestions() {{
            document.getElementById('searchSuggestions').style.display = 'none';
        }}

        function applySuggestion(suggestion) {{
            document.getElementById('globalSearchInput').value = suggestion;
            hideSuggestions();
            performSearch(suggestion);
        }}

        async function performSearch(query) {{
            if (!query) {{
                query = document.getElementById('globalSearchInput').value.trim();
            }

            if (!query) {{
                UI.showToast('Please enter a search term', 'warning');
                return;
            }

            currentSearchQuery = query;
            showLoadingState();

            try {{
                const token = localStorage.getItem('accessToken');
                const searchParams = new URLSearchParams({{
                    q: query,
                    ...currentFilters
                }});

                const response = await fetch(`/api/search?${{searchParams}}`, {{
                    headers: {{ 'Authorization': `Bearer ${{token}}` }}
                }});

                if (response.ok) {{
                    const results = await response.json();
                    displaySearchResults(results, query);
                }} else {{
                    showSearchError('Search failed. Please try again.');
                }
            }} catch (error) {{
                showSearchError('Network error. Please check your connection.');
            }}

            hideLoadingState();
        }}

        function showLoadingState() {{
            document.getElementById('searchEmpty').style.display = 'none';
            document.getElementById('searchResults').style.display = 'none';
            document.getElementById('searchLoading').style.display = 'block';
        }}

        function hideLoadingState() {{
            document.getElementById('searchLoading').style.display = 'none';
        }}

        function displaySearchResults(results, query) {{
            searchResults = results.results || [];
            currentPage = 1;

            document.getElementById('searchResults').style.display = 'block';
            document.getElementById('searchEmpty').style.display = 'none';

            // Update results header
            document.getElementById('resultsCount').textContent = results.total || 0;
            document.getElementById('searchQuery').textContent = query;
            document.getElementById('searchTime').textContent = results.time ? `(${results.time}ms)` : '';

            // Render current page
            renderResultsPage();

            // Update pagination
            updatePagination();
        }}

        function renderResultsPage() {{
            const startIndex = (currentPage - 1) * resultsPerPage;
            const endIndex = startIndex + resultsPerPage;
            const pageResults = searchResults.slice(startIndex, endIndex);

            const resultsList = document.getElementById('resultsList');
            resultsList.innerHTML = '';

            if (pageResults.length === 0) {{
                resultsList.innerHTML = '<div class="no-results">No results found for your search.</div>';
                return;
            }}

            pageResults.forEach(result => {{
                const resultEl = createResultElement(result);
                resultsList.appendChild(resultEl);
            }});
        }}

        function createResultElement(result) {{
            const resultDiv = document.createElement('div');
            resultDiv.className = `search-result result-${{result.type}}`;
            resultDiv.onclick = () => navigateToResult(result);

            resultDiv.innerHTML = `
                <div class="result-header">
                    <div class="result-title">${{highlightQuery(result.title, currentSearchQuery)}}</div>
                    <div class="result-type">${{getTypeLabel(result.type)}}</div>
                </div>
                <div class="result-preview">${{highlightQuery(result.preview, currentSearchQuery)}}</div>
                <div class="result-meta">
                    <span class="result-date">${{formatDate(result.date)}}</span>
                    ${{result.tags ? `<div class="result-tags">${{result.tags.map(tag => `<span class="tag">${{tag}}</span>`).join('')}}</div>` : ''}}
                    <span class="result-score" title="Relevance score">${{result.score || 0}}%</span>
                </div>
            `;

            return resultDiv;
        }}

        function highlightQuery(text, query) {{
            if (!query || !text) return text;

            const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\\\$&')})`, 'gi');
            return text.replace(regex, '<mark>$1</mark>');
        }}

        function getTypeLabel(type) {{
            const labels = {{
                'chat': '💬 Chat',
                'research': '🔬 Research',
                'knowledge': '📚 Knowledge',
                'file': '📄 File'
            }};
            return labels[type] || type;
        }}

        function navigateToResult(result) {{
            switch (result.type) {{
                case 'chat':
                    window.location.href = `/chat/${{result.id}}`;
                    break;
                case 'research':
                    window.location.href = `/research`;
                    break;
                case 'knowledge':
                    window.location.href = `/knowledge`;
                    break;
                default:
                    UI.showToast('Navigation not available for this result type', 'info');
            }}
        }}

        function updatePagination() {{
            const totalPages = Math.ceil(searchResults.length / resultsPerPage);
            const pagination = document.getElementById('resultsPagination');

            if (totalPages <= 1) {{
                pagination.style.display = 'none';
                return;
            }}

            pagination.style.display = 'flex';

            document.getElementById('currentPage').textContent = currentPage;
            document.getElementById('totalPages').textContent = totalPages;

            document.getElementById('prevPageBtn').disabled = currentPage === 1;
            document.getElementById('nextPageBtn').disabled = currentPage === totalPages;
        }}

        function changePage(delta) {{
            currentPage += delta;
            renderResultsPage();
            updatePagination();
        }}

        function filterByType(type) {{
            document.querySelectorAll('.filter-pill').forEach(pill => {{
                pill.classList.remove('active');
            }});
            event.target.classList.add('active');

            // Implement type filtering
            UI.showToast(`${{type}} filter coming soon!`, 'info');
        }}

        function updateFilters() {{
            currentFilters = {{
                types: Array.from(document.querySelectorAll('.checkbox-label input:checked')).map(cb => cb.id.replace('search', '').toLowerCase()),
                dateRange: document.getElementById('dateRange').value,
                sortOrder: document.getElementById('sortOrder').value,
                exactMatch: document.getElementById('exactMatch').checked,
                caseSensitive: document.getElementById('caseSensitive').checked,
                includeArchived: document.getElementById('includeArchived').checked
            }};
        }}

        function handleDateRangeChange(e) {{
            const customRange = document.getElementById('customDateRange');
            customRange.style.display = e.target.value === 'custom' ? 'block' : 'none';
            updateFilters();
        }}

        function clearSearch() {{
            document.getElementById('globalSearchInput').value = '';
            document.getElementById('searchResults').style.display = 'none';
            document.getElementById('searchEmpty').style.display = 'block';
            currentSearchQuery = '';
            searchResults = [];
        }}

        function showSearchError(message) {{
            UI.showToast(message, 'error');
            document.getElementById('searchEmpty').style.display = 'block';
        }}

        function toggleSidebar() {{
            document.querySelector('.sidebar').classList.toggle('show');
        }}

        // Placeholder functions
        function exportResults() {{ UI.showToast('Export functionality coming soon!', 'info'); }}
        function saveSearch() {{ UI.showToast('Save search functionality coming soon!', 'info'); }}
    </script>
</body>
</html>"""

def modern_admin_page():
    return """<html><body><h1>Admin Panel - Coming Soon</h1></body></html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)