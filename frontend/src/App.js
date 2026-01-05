import React, { Suspense, lazy, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ErrorBoundary from './ErrorBoundary';

// Lazy load components for code splitting
const ResearchControls = lazy(() => import('./ResearchControls'));
const ResearchProgress = lazy(() => import('./ResearchProgress'));
const ResearchHistory = lazy(() => import('./ResearchHistory'));
const MultiAgentDashboard = lazy(() => import('./MultiAgentDashboard'));
const SettingsPanel = lazy(() => import('./SettingsPanel'));
const ChatSessions = lazy(() => import('./ChatSessions'));
const Chat = lazy(() => import('./Chat'));
const FileUpload = lazy(() => import('./FileUpload'));
const DocumentQATab = lazy(() => import('./DocumentQATab'));
import MainSidebar from './MainSidebar';
const HomePage = lazy(() => import('./HomePage'));

function App() {
  const [currentTaskId, setCurrentTaskId] = useState(null);
  const [isResearching, setIsResearching] = useState(false);
  const [researchResults, setResearchResults] = useState(null);
  const [activeMode, setActiveMode] = useState('home');
  const [theme, setTheme] = useState('dark');
  const [currentChatSessionId, setCurrentChatSessionId] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedModel, setSelectedModel] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [appSettings, setAppSettings] = useState({});

  useEffect(() => {
    // Check for existing research sessions on load
    checkExistingSession();
    // Load settings
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch('/api/settings');
      if (response.ok) {
        const settings = await response.json();
        setAppSettings(settings);
        setTheme(settings.theme || 'dark');
        applyTheme(settings.theme || 'dark');
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const applyTheme = (newTheme) => {
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  const checkExistingSession = async () => {
    try {
      // Could implement session persistence here
      // For now, just clear any stale state
      setCurrentTaskId(null);
      setIsResearching(false);
      setResearchResults(null);
    } catch (error) {
      console.error('Error checking existing session:', error);
    }
  };

  const handleStartResearch = async (topic, depth) => {
    try {
      const response = await fetch('/api/research/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          depth,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to start research');
      }

      const data = await response.json();
      setCurrentTaskId(data.task_id);
      setIsResearching(true);
      setResearchResults(null);

      return data.task_id;
    } catch (error) {
      throw error;
    }
  };

  const handleStopResearch = async (taskId) => {
    try {
      const response = await fetch(`/api/research/${taskId}/stop`, {
        method: 'POST',
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to stop research');
      }

      setIsResearching(false);
      setCurrentTaskId(null);
    } catch (error) {
      console.error('Error stopping research:', error);
      throw error;
    }
  };

  const handleResearchComplete = (results) => {
    setIsResearching(false);
    setResearchResults(results);
  };

  const handleResearchError = (error) => {
    console.error('Research error:', error);
    setIsResearching(false);
  };

  const handleModeChange = (mode) => {
    setActiveMode(mode);
    setShowSettings(false);
    if (mode === 'home') {
      setCurrentChatSessionId(null);
    }
  };

  const handleStartChat = (initialMessage = null) => {
    setActiveMode('chat');
    if (initialMessage) {
      // TODO: Create new chat session with initial message
      console.log('Starting chat with:', initialMessage);
    }
  };

  const handleModelChange = (model) => {
    setSelectedModel(model);
    // TODO: Save model preference
  };

  return (
    <ErrorBoundary>
      <div className="app">
        {/* Sidebar Toggle Button */}
        <button
          className={`sidebar-toggle ${sidebarOpen ? 'shifted' : ''}`}
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label={sidebarOpen ? "Close sidebar" : "Open sidebar"}
        >
          {sidebarOpen ? '✕' : '☰'}
        </button>

        {/* Main Sidebar */}
        <MainSidebar
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen(false)}
          activeMode={activeMode}
          onModeChange={handleModeChange}
          currentChatSessionId={currentChatSessionId}
          onChatSessionSelect={(sessionId) => {
            setCurrentChatSessionId(sessionId);
            setActiveMode('chat');
          }}
          selectedModel={selectedModel}
          onModelChange={handleModelChange}
          onSettingsClick={() => setShowSettings(true)}
        />

        {/* Main Content Area */}
        <div className={`main-content ${!sidebarOpen ? 'sidebar-closed' : ''}`}>
          <AnimatePresence mode="wait">
            <motion.main
              key={activeMode}
              className="app-main"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
            >
              <Suspense fallback={
                <motion.div
                  className="loading-tab"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <div className="spinner"></div>
                  <p>Loading...</p>
                </motion.div>
              }>
                {showSettings ? (
                  <SettingsPanel
                    onSettingsChange={(settings) => {
                      if (settings.theme && settings.theme !== theme) {
                        setTheme(settings.theme);
                        applyTheme(settings.theme);
                      }
                      setShowSettings(false);
                    }}
                    onBack={() => setShowSettings(false)}
                  />
                ) : activeMode === 'home' ? (
                  <HomePage
                    onStartChat={handleStartChat}
                    onStartResearch={() => setActiveMode('research')}
                    selectedModel={selectedModel}
                    onModelChange={handleModelChange}
                    settings={appSettings}
                  />
                ) : activeMode === 'chat' ? (
                  currentChatSessionId ? (
                    <Chat
                      sessionId={currentChatSessionId}
                      onBack={() => setCurrentChatSessionId(null)}
                      selectedModel={selectedModel}
                    />
                  ) : (
                    <ChatSessions
                      onSessionSelect={(sessionId) => {
                        setCurrentChatSessionId(sessionId);
                      }}
                      currentSessionId={currentChatSessionId}
                    />
                  )
                ) : activeMode === 'research' ? (
                  <>
                    <ResearchControls
                      onStartResearch={handleStartResearch}
                      onStopResearch={handleStopResearch}
                      currentTask={currentTaskId}
                      isResearching={isResearching}
                    />

                    {currentTaskId && (
                      <ResearchProgress
                        taskId={currentTaskId}
                        onComplete={handleResearchComplete}
                        onError={handleResearchError}
                      />
                    )}

                    <ResearchHistory
                      onResumeSession={(taskId) => {
                        setCurrentTaskId(taskId);
                        setIsResearching(true);
                        setResearchResults(null);
                      }}
                      onDeleteSession={(taskId) => {
                        if (currentTaskId === taskId) {
                          setCurrentTaskId(null);
                          setIsResearching(false);
                          setResearchResults(null);
                        }
                      }}
                    />

                    {researchResults && (
                      <div className="research-results">
                        <div className="results-summary">
                          <div className="result-item">
                            <span className="label">Topics Analyzed:</span>
                            <span className="value">{researchResults.total_topics}</span>
                          </div>
                          <div className="result-item">
                            <span className="label">Findings:</span>
                            <span className="value">{researchResults.findings_count}</span>
                          </div>
                          <div className="result-item">
                            <span className="label">Completion Time:</span>
                            <span className="value">
                              {researchResults.start_time ?
                                new Date(researchResults.last_update).getTime() - new Date(researchResults.start_time).getTime() > 0 ?
                                  `${Math.round((new Date(researchResults.last_update).getTime() - new Date(researchResults.start_time).getTime()) / 1000 / 60)} minutes` :
                                  'Just completed' :
                                'Unknown'
                              }
                            </span>
                          </div>
                        </div>
                        <div className="results-message">
                          <p>{researchResults.result}</p>
                        </div>
                      </div>
                    )}
                  </>
                ) : activeMode === 'qa' ? (
                  <DocumentQATab />
                ) : activeMode === 'documents' ? (
                  <FileUpload
                    onFileUpload={(file, fileInfo) => {
                      console.log('File uploaded:', fileInfo);
                      // In Phase 5, this will trigger document processing
                    }}
                  />
                ) : activeMode === 'dashboard' ? (
                  <MultiAgentDashboard />
                ) : null}
              </Suspense>
            </motion.main>
          </AnimatePresence>
        </div>

        <style>{`
          :root {
            /* Light theme */
            --bg-primary: #ffffff;
            --bg-secondary: #f8f9fa;
            --bg-tertiary: #e9ecef;
            --text-primary: #333333;
            --text-secondary: #666666;
            --text-muted: #999999;
            --border-color: #e9ecef;
            --shadow: rgba(0,0,0,0.1);
            --accent: #007bff;
            --success: #28a745;
            --warning: #ffc107;
            --error: #dc3545;
            --info: #17a2b8;
          }

          [data-theme="dark"] {
            /* Dark theme */
            --bg-primary: #1a1a1a;
            --bg-secondary: #2d2d2d;
            --bg-tertiary: #404040;
            --text-primary: #ffffff;
            --text-secondary: #cccccc;
            --text-muted: #888888;
            --border-color: #404040;
            --shadow: rgba(0,0,0,0.3);
            --accent: #4dabf7;
            --success: #51cf66;
            --warning: #ffd43b;
            --error: #ff6b6b;
            --info: #74c0fc;
          }

          * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
          }

          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
              'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            background: var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.6;
            transition: background-color 0.3s ease, color 0.3s ease;
          }

          .app {
            display: flex;
            min-height: 100vh;
            background: var(--bg-secondary);
          }

          .sidebar-toggle {
            position: fixed;
            top: max(10px, 1vh);
            left: max(10px, 1vw);
            z-index: 1001;
            background: var(--accent);
            color: white;
            border: none;
            border-radius: min(8px, 1vh);
            padding: clamp(8px, 2vw, 12px);
            font-size: clamp(16px, 3vw, 18px);
            cursor: pointer;
            box-shadow: 0 4px 12px var(--shadow);
            transition: all 0.2s ease;
            width: auto;
            height: auto;
            min-width: 44px;
            min-height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
          }

          .sidebar-toggle:hover {
            background: #0056b3;
            transform: scale(1.05);
          }

          /* Extra small screens (< 480px) */
          @media (max-width: 480px) {
            .sidebar-toggle {
              top: 8px;
              left: 8px;
              padding: 10px;
              font-size: 16px;
              min-width: 40px;
              min-height: 40px;
            }
          }

          /* Small screens (481px - 768px) */
          @media (min-width: 481px) and (max-width: 768px) {
            .sidebar-toggle {
              top: 15px;
              left: 15px;
              padding: 11px;
              font-size: 17px;
            }
          }

          /* Medium screens (769px - 1024px) */
          @media (min-width: 769px) and (max-width: 1024px) {
            .sidebar-toggle {
              left: 20px;
              transition: left 0.3s ease;
            }

            .sidebar-toggle.shifted {
              left: 340px;
            }
          }

          /* Large screens (1025px - 1440px) */
          @media (min-width: 1025px) and (max-width: 1440px) {
            .sidebar-toggle {
              left: 20px;
              transition: left 0.3s ease;
            }

            .sidebar-toggle.shifted {
              left: 340px;
            }
          }

          /* Extra large screens (> 1440px) */
          @media (min-width: 1441px) {
            .sidebar-toggle {
              left: clamp(20px, 2vw, 40px);
              transition: left 0.3s ease;
            }

            .sidebar-toggle.shifted {
              left: clamp(340px, calc(320px + 2vw), 400px);
            }
          }

          .sidebar-loading {
            width: 320px;
            height: 100vh;
            background: var(--bg-secondary);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
          }

          .main-content {
            flex: 1;
            margin-left: 320px;
            transition: margin-left 0.3s ease;
            min-height: 100vh;
            padding: clamp(10px, 2vw, 20px);
            box-sizing: border-box;
          }

          .main-content.sidebar-closed {
            margin-left: 0;
          }

          /* Extra small screens (< 480px) */
          @media (max-width: 480px) {
            .main-content {
              margin-left: 0;
              padding: 10px;
            }
          }

          /* Small screens (481px - 768px) */
          @media (min-width: 481px) and (max-width: 768px) {
            .main-content {
              margin-left: 0;
              padding: 15px;
            }
          }

          /* Medium screens (769px - 1024px) */
          @media (min-width: 769px) and (max-width: 1024px) {
            .main-content {
              margin-left: 320px;
            }

            .main-content.sidebar-closed {
              margin-left: 0;
            }
          }

          /* Large screens (1025px - 1440px) */
          @media (min-width: 1025px) and (max-width: 1440px) {
            .main-content {
              margin-left: 320px;
            }

            .main-content.sidebar-closed {
              margin-left: 0;
            }
          }

          /* Extra large screens (> 1440px) */
          @media (min-width: 1441px) {
            .main-content {
              margin-left: clamp(320px, 25vw, 400px);
            }

            .main-content.sidebar-closed {
              margin-left: 0;
            }
          }

        .app-main {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

          .research-results {
            background: var(--bg-primary);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px var(--shadow);
          }

          .research-results h3 {
            color: var(--success);
            margin-bottom: 20px;
          }

          .results-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
          }

          .result-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
          }

          .result-item .label {
            font-weight: 500;
            color: #666;
          }

          .result-item .value {
            font-weight: 600;
            color: #007bff;
          }

          .results-message {
            padding: 15px;
            background: var(--success);
            background: rgba(40, 167, 69, 0.1);
            border: 1px solid var(--success);
            border-radius: 6px;
            color: var(--text-primary);
          }

          .results-message p {
            margin: 0;
            font-size: 16px;
          }

        /* Skeleton Loading Styles */
        .skeleton {
          background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--bg-secondary) 50%, var(--bg-tertiary) 75%);
          background-size: 200% 100%;
          animation: skeleton-loading 1.5s infinite;
          border-radius: 4px;
        }

        .skeleton-pulse {
          animation: skeleton-pulse 1.5s ease-in-out infinite;
        }

        .skeleton-wave {
          animation: skeleton-wave 1.5s ease-in-out infinite;
        }

        .skeleton-text {
          border-radius: 4px;
          margin-bottom: 8px;
        }

        .skeleton-rectangular {
          border-radius: 4px;
        }

        .skeleton-circular {
          border-radius: 50%;
        }

        .skeleton-avatar {
          border-radius: 50%;
          display: inline-block;
        }

        .skeleton-text-block {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .skeleton-card {
          border: 1px solid var(--border-color);
          border-radius: 8px;
          padding: 16px;
          background: var(--bg-primary);
        }

        .skeleton-card-title {
          margin-bottom: 12px;
        }

        .skeleton-card-content {
          margin-bottom: 12px;
        }

        .skeleton-card-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .skeleton-table {
          border: 1px solid var(--border-color);
          border-radius: 4px;
          overflow: hidden;
        }

        .skeleton-table-header,
        .skeleton-table-row {
          display: flex;
          gap: 12px;
          padding: 12px;
          border-bottom: 1px solid var(--border-color);
        }

        .skeleton-table-row:last-child {
          border-bottom: none;
        }

        .skeleton-button {
          border-radius: 6px;
        }

        @keyframes skeleton-loading {
          0% {
            background-position: -200% 0;
          }
          100% {
            background-position: 200% 0;
          }
        }

        @keyframes skeleton-pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }

        @keyframes skeleton-wave {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }

        .loading-tab {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 60px 20px;
          text-align: center;
        }

        .loading-tab .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid var(--bg-tertiary);
          border-top: 4px solid var(--accent);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 20px;
        }

        .loading-tab p {
          color: var(--text-secondary);
          font-size: 16px;
        }

        @media (max-width: 768px) {
          .app {
            padding: 10px;
          }

          .app-header h1 {
            font-size: 2rem;
          }

          .results-summary {
            grid-template-columns: 1fr;
          }

          .loading-tab {
            padding: 40px 10px;
          }

          .loading-tab .spinner {
            width: 30px;
            height: 30px;
          }
        }
        `}</style>
      </div>
    </ErrorBoundary>
  );
}

export default App;