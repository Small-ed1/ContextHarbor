import React, { useState, useRef, useEffect } from 'react';
import RichTextMessage from './RichTextMessage';
import ChatMessageInput from './ChatMessageInput';
import Skeleton, { SkeletonText } from './Skeleton';

const Chat = ({ sessionId, onBack, onToggleResearch, selectedModel }) => {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [researchMode, setResearchMode] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    loadChatSession();
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadChatSession = async () => {
    if (!sessionId) return;

    try {
      setIsLoading(true);
      const response = await fetch(`/api/chats/${sessionId}`);
      if (response.ok) {
        const chatData = await response.json();
        setMessages(chatData.messages || []);
        setError(null);
      } else {
        setError('Failed to load chat session');
      }
    } catch (err) {
      setError(`Error loading chat: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: currentMessage.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          mode: researchMode ? 'research' : 'chat',
          project: 'default',
          model: selectedModel || undefined,
          history: messages.slice(-10).map(m => ({  // Last 10 messages for context
            type: m.type,
            content: m.content
          })),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: data.response,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error(`API error: ${response.status}`);
      }
    } catch (err) {
      setError(`Failed to send message: ${err.message}`);
      setIsLoading(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const renderMessage = (message) => {
    if (message.type === 'user') {
      return (
        <div
          className="message user-message"
        >
          <div className="message-content">
            <div className="message-text">
              {message.content}
            </div>
            <div className="message-tail"></div>
          </div>
          <div className="message-meta">
            <span className="timestamp">{formatTimestamp(message.timestamp)}</span>
            <span className="message-status">✓</span>
           </div>
        </div>
      );
    } else {
      return (
        <div
          className="message ai-message"
        >
          <div className="message-header">
            <div className="ai-avatar">
              <div className="avatar-gradient">
                <span className="avatar-icon">🤖</span>
              </div>
            </div>
            <div className="ai-info">
              <span className="ai-name">AI Assistant</span>
              <span className="model-badge">{selectedModel || 'Llama 3.2'}</span>
            </div>
          </div>

          <div className="message-content">
            <div className="answer-text">
              <RichTextMessage content={message.content} />
            </div>
            <div className="message-tail"></div>
          </div>

          <div className="message-meta">
            <span className="timestamp">{formatTimestamp(message.timestamp)}</span>
            <div className="message-actions">
              <button className="action-btn" title="Copy message">📋</button>
              <button className="action-btn" title="Regenerate">🔄</button>
            </div>
           </div>
        </div>
      );
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <button onClick={onBack} className="back-button">
          ← Back to Sessions
        </button>
        <div className="chat-info">
          <h3>Chat Session</h3>
          <p>Session ID: {sessionId}</p>
          {selectedModel && <p>Model: {selectedModel}</p>}
        </div>
        <div className="chat-controls">
          <label className="research-toggle">
            <input
              type="checkbox"
              checked={researchMode}
              onChange={(e) => setResearchMode(e.target.checked)}
            />
            <span className="toggle-label">Deep Research Mode</span>
          </label>
        </div>
      </div>

      <div className="chat-container">
        <div className="messages-area">
           {messages.length === 0 && !isLoading ? (
              <div
                className="welcome-message"
              >
               <div className="welcome-illustration">
                 <div className="welcome-glow"></div>
                 <div className="welcome-icon">🚀</div>
               </div>
               <h4>Welcome to your AI Chat!</h4>
               <p>I'm here to help with questions, research, creative tasks, and more. What would you like to explore today?</p>
               <div className="suggestion-chips">
                 <button className="chip" onClick={() => setCurrentMessage("Explain quantum computing in simple terms")}>
                   💡 Explain quantum computing
                 </button>
                 <button className="chip" onClick={() => setCurrentMessage("Write a creative story about space exploration")}>
                   📖 Write a story
                 </button>
                 <button className="chip" onClick={() => setCurrentMessage("Help me debug this code")}>
                   🐛 Debug code
                 </button>
                 <button className="chip" onClick={() => setResearchMode(true)}>
                   🔬 Research mode
                 </button>
               </div>
        </div>
           ) : (
            <>
              {messages.map(message => (
                <div key={message.id}>
                  {renderMessage(message)}
                </div>
              ))}

               {isLoading && (
                  <div
                    className="message ai-message typing"
                  >
                   <div className="message-header">
                     <div className="ai-avatar">
                       <div className="avatar-gradient">
                         <span className="avatar-icon">🤖</span>
                       </div>
                     </div>
                     <div className="ai-info">
                       <span className="ai-name">AI Assistant</span>
                       <span className="typing-indicator">
                         <span></span>
                         <span></span>
                         <span></span>
                       </span>
                     </div>
                   </div>
                   <div className="message-content">
                     <div className="typing-placeholder">
                       <div className="typing-dots">
                         <span></span>
                         <span></span>
                         <span></span>
                       </div>
                       <span className="typing-text">AI is thinking...</span>
                     </div>
                   </div>
        </div>
               )}

              {error && (
                <div className="error-message">
                  <span>⚠️ {error}</span>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        <div className="input-area">
            <div className="message-input-container">
              <ChatMessageInput
                onSendMessage={(message) => {
                  // For now, treat as plain text. Later can parse HTML if needed
                  setCurrentMessage(message);
                  sendMessage();
                }}
                placeholder={researchMode ? "Ask a research question..." : "Type your message..."}
              />
              <div className="input-actions">
                <button
                  className={`mode-toggle ${researchMode ? 'active' : ''}`}
                  onClick={() => setResearchMode(!researchMode)}
                  title={researchMode ? 'Switch to chat mode' : 'Switch to research mode'}
                  disabled={isLoading}
                >
                  {researchMode ? '🔬' : '💬'}
                </button>
              </div>
              {researchMode && (
                <div className="research-notice">
                  <span className="notice-icon">🔬</span>
                  <span className="notice-text">Research mode enabled - This may take longer for comprehensive analysis</span>
                </div>
              )}
            </div>
          </div>
      </div>

       <style>{`
         .chat-interface {
           height: 100%;
           display: flex;
           flex-direction: column;
           background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
         }

         .chat-header {
           display: flex;
           align-items: center;
           gap: clamp(15px, 3vw, 20px);
           padding: clamp(15px, 3vw, 20px);
           border-bottom: 1px solid var(--border-color);
           background: var(--bg-primary);
           backdrop-filter: blur(10px);
           box-shadow: 0 2px 20px var(--shadow);
           flex-wrap: wrap;
         }

         .back-button {
           padding: clamp(8px, 2vw, 10px) clamp(16px, 3vw, 20px);
           background: linear-gradient(135deg, var(--accent), #4dabf7);
           color: white;
           border: none;
           border-radius: clamp(8px, 2vw, 12px);
           cursor: pointer;
           font-size: clamp(12px, 2.5vw, 14px);
           font-weight: 600;
           white-space: nowrap;
           transition: all 0.2s ease;
           box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
         }

         .back-button:hover {
           transform: translateY(-2px);
           box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
         }

         .chat-info h3 {
           margin: 0;
           color: var(--text-primary);
           font-size: clamp(18px, 3vw, 20px);
           font-weight: 600;
           background: linear-gradient(135deg, var(--text-primary), var(--text-secondary));
           -webkit-background-clip: text;
           -webkit-text-fill-color: transparent;
           background-clip: text;
         }

         .chat-info p {
           margin: clamp(4px, 1vh, 6px) 0 0 0;
           color: var(--text-secondary);
           font-size: clamp(12px, 2.5vw, 14px);
         }

         .chat-controls {
           margin-left: auto;
           display: flex;
           align-items: center;
           gap: 15px;
         }

         .research-toggle {
           display: flex;
           align-items: center;
           gap: clamp(8px, 2vw, 10px);
           cursor: pointer;
           font-size: clamp(12px, 2.5vw, 14px);
           color: var(--text-secondary);
           padding: 8px 12px;
           border-radius: 20px;
           transition: all 0.2s ease;
           background: var(--bg-tertiary);
         }

         .research-toggle:hover {
           background: var(--bg-secondary);
         }

         .research-toggle input[type="checkbox"] {
           width: clamp(16px, 3vw, 18px);
           height: clamp(16px, 3vw, 18px);
           accent-color: var(--accent);
         }

         .toggle-label {
           font-weight: 500;
         }

         .chat-container {
           flex: 1;
           display: flex;
           flex-direction: column;
           overflow: hidden;
         }

         .messages-area {
           flex: 1;
           overflow-y: auto;
           padding: clamp(20px, 3vw, 24px);
           display: flex;
           flex-direction: column;
           gap: clamp(20px, 3vh, 24px);
           scroll-behavior: smooth;
         }

         .messages-area::-webkit-scrollbar {
           width: 6px;
         }

         .messages-area::-webkit-scrollbar-track {
           background: var(--bg-tertiary);
           border-radius: 3px;
         }

         .messages-area::-webkit-scrollbar-thumb {
           background: var(--border-color);
           border-radius: 3px;
         }

         .messages-area::-webkit-scrollbar-thumb:hover {
           background: var(--text-muted);
         }

         .welcome-message {
           text-align: center;
           padding: clamp(60px, 20vh, 80px) clamp(20px, 5vw, 24px);
           color: var(--text-secondary);
           max-width: 600px;
           margin: 0 auto;
         }

         .welcome-illustration {
           position: relative;
           display: inline-block;
           margin-bottom: clamp(24px, 6vh, 32px);
         }

         .welcome-glow {
           position: absolute;
           top: -10px;
           left: -10px;
           right: -10px;
           bottom: -10px;
           background: radial-gradient(circle, rgba(74, 144, 226, 0.3) 0%, transparent 70%);
           border-radius: 50%;
           animation: pulse 2s ease-in-out infinite;
         }

         .welcome-icon {
           font-size: clamp(48px, 12vw, 64px);
           position: relative;
           z-index: 1;
           animation: float 3s ease-in-out infinite;
         }

         @keyframes pulse {
           0%, 100% { transform: scale(1); opacity: 0.7; }
           50% { transform: scale(1.1); opacity: 1; }
         }

         @keyframes float {
           0%, 100% { transform: translateY(0px); }
           50% { transform: translateY(-10px); }
         }

         .welcome-message h4 {
           margin: 0 0 clamp(12px, 3vh, 16px) 0;
           color: var(--text-primary);
           font-size: clamp(24px, 5vw, 28px);
           font-weight: 600;
         }

         .welcome-message p {
           margin: 0 0 clamp(24px, 6vh, 32px) 0;
           font-size: clamp(16px, 3vw, 18px);
           line-height: 1.6;
         }

         .suggestion-chips {
           display: flex;
           flex-wrap: wrap;
           gap: 12px;
           justify-content: center;
         }

         .chip {
           padding: 10px 16px;
           background: var(--bg-primary);
           border: 1px solid var(--border-color);
           border-radius: 20px;
           color: var(--text-primary);
           font-size: 14px;
           cursor: pointer;
           transition: all 0.2s ease;
           white-space: nowrap;
           box-shadow: 0 2px 8px var(--shadow);
         }

         .chip:hover {
           transform: translateY(-2px);
           box-shadow: 0 4px 16px var(--shadow);
           border-color: var(--accent);
         }

         .message {
           display: flex;
           flex-direction: column;
           gap: clamp(8px, 2vh, 10px);
           max-width: min(85%, 700px);
           width: 100%;
           position: relative;
         }

         .user-message {
           align-self: flex-end;
           align-items: flex-end;
         }

         .ai-message {
           align-self: flex-start;
           align-items: flex-start;
         }

         .message-header {
           display: flex;
           align-items: center;
           gap: clamp(10px, 2vw, 12px);
           margin-bottom: 4px;
         }

         .ai-avatar {
           position: relative;
         }

         .avatar-gradient {
           width: clamp(36px, 7vw, 40px);
           height: clamp(36px, 7vw, 40px);
           border-radius: 50%;
           background: linear-gradient(135deg, var(--accent), #4dabf7);
           display: flex;
           align-items: center;
           justify-content: center;
           box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
           transition: all 0.2s ease;
         }

         .avatar-gradient:hover {
           transform: scale(1.1);
         }

         .avatar-icon {
           font-size: clamp(16px, 3vw, 18px);
           filter: drop-shadow(0 1px 2px rgba(0,0,0,0.1));
         }

         .ai-name {
           font-weight: 600;
           color: var(--text-primary);
           font-size: clamp(15px, 2.5vw, 16px);
         }

         .model-badge {
           font-size: 11px;
           color: var(--text-muted);
           background: var(--bg-tertiary);
           padding: 2px 6px;
           border-radius: 8px;
           margin-left: 8px;
           font-weight: 500;
         }

         .typing-indicator {
           display: flex;
           gap: 2px;
           margin-left: 8px;
         }

         .typing-indicator span {
           width: 4px;
           height: 4px;
           border-radius: 50%;
           background: var(--accent);
           animation: typing 1.4s ease-in-out infinite;
         }

         .typing-indicator span:nth-child(1) { animation-delay: 0s; }
         .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
         .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

         @keyframes typing {
           0%, 60%, 100% { transform: scale(0.8); opacity: 0.5; }
           30% { transform: scale(1); opacity: 1; }
         }

         .message-content {
           position: relative;
           padding: clamp(16px, 3vw, 20px);
           border-radius: clamp(16px, 4vw, 20px);
           background: var(--bg-primary);
           border: 1px solid var(--border-color);
           box-shadow: 0 4px 20px var(--shadow);
           word-wrap: break-word;
           overflow-wrap: break-word;
           transition: all 0.2s ease;
         }

         .user-message .message-content {
           background: linear-gradient(135deg, var(--accent), #4dabf7);
           color: white;
           border: none;
           box-shadow: 0 4px 20px rgba(0, 123, 255, 0.3);
         }

         .message-tail {
           position: absolute;
           width: 0;
           height: 0;
           border: 8px solid transparent;
         }

         .user-message .message-tail {
           right: -8px;
           bottom: 16px;
           border-left-color: #4dabf7;
           border-right: none;
         }

         .ai-message .message-tail {
           left: -8px;
           bottom: 16px;
           border-right-color: var(--bg-primary);
           border-left: none;
         }

         .message-text {
           line-height: 1.6;
           font-size: clamp(15px, 2.5vw, 16px);
           white-space: pre-wrap;
         }

         .answer-text {
           line-height: 1.7;
           font-size: clamp(15px, 2.5vw, 16px);
         }

         .typing-placeholder {
           display: flex;
           align-items: center;
           gap: 12px;
           color: var(--text-secondary);
           font-style: italic;
         }

         .typing-dots {
           display: flex;
           gap: 4px;
         }

         .typing-dots span {
           width: 6px;
           height: 6px;
           border-radius: 50%;
           background: var(--accent);
           animation: typing-dots 1.4s ease-in-out infinite;
         }

         .typing-dots span:nth-child(1) { animation-delay: 0s; }
         .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
         .typing-dots span:nth-child(3) { animation-delay: 0.4s; }

         @keyframes typing-dots {
           0%, 60%, 100% { transform: scale(0.8); opacity: 0.5; }
           30% { transform: scale(1.2); opacity: 1; }
         }

         .typing-text {
           font-size: 14px;
         }

         .message-meta {
           display: flex;
           align-items: center;
           justify-content: space-between;
           font-size: clamp(11px, 2vw, 12px);
           color: var(--text-muted);
           padding: 0 clamp(4px, 1vw, 6px);
           margin-top: 4px;
         }

         .user-message .message-meta {
           justify-content: flex-end;
         }

         .message-status {
           margin-left: 8px;
           color: #28a745;
           font-weight: bold;
         }

         .message-actions {
           display: flex;
           gap: 6px;
         }

         .action-btn {
           background: none;
           border: none;
           color: var(--text-muted);
           cursor: pointer;
           padding: 4px;
           border-radius: 4px;
           font-size: 12px;
           transition: all 0.2s ease;
           opacity: 0.7;
         }

         .action-btn:hover {
           background: var(--bg-tertiary);
           opacity: 1;
           transform: scale(1.1);
         }

         .error-message {
           padding: 16px;
           background: linear-gradient(135deg, rgba(220, 53, 69, 0.1), rgba(220, 53, 69, 0.05));
           border: 1px solid var(--error);
           border-radius: 12px;
           color: var(--error);
           text-align: center;
           box-shadow: 0 4px 16px rgba(220, 53, 69, 0.1);
           backdrop-filter: blur(10px);
         }

         .input-area {
           padding: clamp(20px, 3vw, 24px);
           border-top: 1px solid var(--border-color);
           background: var(--bg-primary);
           backdrop-filter: blur(10px);
           box-shadow: 0 -4px 20px var(--shadow);
         }

         .message-input-container {
           max-width: 900px;
           margin: 0 auto;
         }

         .input-wrapper {
           display: flex;
           align-items: flex-end;
           gap: 12px;
           background: var(--bg-secondary);
           border: 2px solid var(--border-color);
           border-radius: 24px;
           padding: 4px;
           transition: all 0.2s ease;
           box-shadow: 0 4px 16px var(--shadow);
         }

         .input-wrapper:focus-within {
           border-color: var(--accent);
           box-shadow: 0 4px 24px rgba(0, 123, 255, 0.2);
         }

         .message-input {
           flex: 1;
           padding: 16px 20px;
           border: none;
           background: transparent;
           color: var(--text-primary);
           font-size: 16px;
           font-family: inherit;
           resize: none;
           min-height: 20px;
           max-height: 120px;
           line-height: 1.5;
           outline: none;
         }

         .message-input::placeholder {
           color: var(--text-secondary);
         }

         .message-input:disabled {
           opacity: 0.6;
           cursor: not-allowed;
         }

         .input-actions {
           display: flex;
           align-items: center;
           gap: 8px;
           padding-right: 8px;
         }

         .mode-toggle {
           width: 40px;
           height: 40px;
           border: none;
           border-radius: 50%;
           background: var(--bg-tertiary);
           color: var(--text-secondary);
           cursor: pointer;
           display: flex;
           align-items: center;
           justify-content: center;
           font-size: 18px;
           transition: all 0.2s ease;
         }

         .mode-toggle:hover:not(:disabled) {
           background: var(--bg-primary);
           transform: scale(1.1);
         }

         .mode-toggle.active {
           background: var(--accent);
           color: white;
           box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
         }

         .mode-toggle:disabled {
           opacity: 0.5;
           cursor: not-allowed;
         }

         .send-button {
           width: 48px;
           height: 48px;
           border: none;
           border-radius: 50%;
           background: linear-gradient(135deg, var(--accent), #4dabf7);
           color: white;
           cursor: pointer;
           display: flex;
           align-items: center;
           justify-content: center;
           font-size: 18px;
           transition: all 0.2s ease;
           box-shadow: 0 4px 16px rgba(0, 123, 255, 0.3);
         }

         .send-button:hover:not(:disabled) {
           transform: scale(1.1);
           box-shadow: 0 6px 24px rgba(0, 123, 255, 0.4);
         }

         .send-button:disabled {
           background: var(--text-secondary);
           cursor: not-allowed;
           transform: none;
           box-shadow: none;
         }

         .send-spinner {
           width: 20px;
           height: 20px;
           border: 2px solid rgba(255, 255, 255, 0.3);
           border-top: 2px solid white;
           border-radius: 50%;
           animation: spin 1s linear infinite;
         }

         @keyframes spin {
           0% { transform: rotate(0deg); }
           50% { transform: rotate(180deg); }
           100% { transform: rotate(360deg); }
         }

         .research-notice {
           display: flex;
           align-items: center;
           gap: 8px;
           margin-top: 12px;
           padding: 10px 16px;
           background: rgba(255, 193, 7, 0.1);
           border: 1px solid var(--warning);
           border-radius: 12px;
           color: var(--text-primary);
           font-size: 14px;
         }

         .notice-icon {
           font-size: 16px;
         }

         .notice-text {
           flex: 1;
         }

         /* Responsive Design */
         @media (max-width: 768px) {
           .chat-header {
             flex-direction: column;
             gap: 16px;
             align-items: stretch;
             padding: 16px;
           }

           .chat-controls {
             margin-left: 0;
             justify-content: center;
           }

           .messages-area {
             padding: 16px;
             gap: 16px;
           }

           .message {
             max-width: 100%;
           }

           .message-content {
             padding: 14px;
           }

           .input-area {
             padding: 16px;
           }

           .input-wrapper {
             flex-direction: column;
             gap: 8px;
             border-radius: 16px;
           }

           .input-actions {
             justify-content: space-between;
             padding: 8px 16px 0 16px;
           }

           .message-input {
             padding: 12px 16px;
           }

           .suggestion-chips {
             flex-direction: column;
             align-items: center;
           }

           .chip {
             width: 100%;
             max-width: 280px;
             justify-content: center;
           }
         }

         @media (max-width: 480px) {
           .welcome-message {
             padding: 40px 16px;
           }

           .welcome-icon {
             font-size: 48px;
           }

           .suggestion-chips {
             gap: 8px;
           }

           .chip {
             padding: 8px 12px;
             font-size: 13px;
           }

           .research-notice {
             flex-direction: column;
             text-align: center;
             gap: 6px;
           }
         }
       `}</style>
    </div>
  );
};

export default Chat;