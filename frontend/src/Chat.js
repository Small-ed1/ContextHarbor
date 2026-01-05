import React, { useState, useRef, useEffect } from 'react';
import RichTextMessage from './RichTextMessage';
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
        <div className="message user-message">
          <div className="message-content">
            <p>{message.content}</p>
          </div>
          <div className="message-meta">
            <span className="timestamp">{formatTimestamp(message.timestamp)}</span>
          </div>
        </div>
      );
    } else {
      return (
        <div className="message ai-message">
          <div className="message-header">
            <div className="ai-avatar">🤖</div>
            <div className="ai-info">
              <span className="ai-name">AI Assistant</span>
            </div>
          </div>

          <div className="message-content">
            <div className="answer-text">
              <RichTextMessage content={message.content} />
            </div>
          </div>

          <div className="message-meta">
            <span className="timestamp">{formatTimestamp(message.timestamp)}</span>
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
            <div className="welcome-message">
              <div className="welcome-icon">💬</div>
              <h4>Start a conversation</h4>
              <p>Type your message below to begin chatting with the AI assistant.</p>
            </div>
          ) : (
            <>
              {messages.map(message => (
                <div key={message.id}>
                  {renderMessage(message)}
                </div>
              ))}

              {isLoading && (
                <div className="message ai-message">
                  <div className="message-header">
                    <div className="ai-avatar">🤖</div>
                    <div className="ai-info">
                      <span className="ai-name">AI Assistant</span>
                    </div>
                  </div>
                  <div className="message-content">
                    <div className="loading-indicator">
                      <Skeleton width="100%" height="1rem" />
                      <Skeleton width="80%" height="1rem" />
                      <Skeleton width="60%" height="1rem" />
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
            <textarea
              ref={inputRef}
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
              disabled={isLoading}
              rows={3}
            />
            <button
              onClick={sendMessage}
              disabled={!currentMessage.trim() || isLoading}
              className="send-button"
            >
              {isLoading ? '⏳' : '📤'}
            </button>
          </div>
        </div>
      </div>

      <style>{`
        .chat-interface {
          height: 100%;
          display: flex;
          flex-direction: column;
        }

        .chat-header {
          display: flex;
          align-items: center;
          gap: clamp(15px, 3vw, 20px);
          padding: clamp(15px, 3vw, 20px);
          border-bottom: 1px solid var(--border-color);
          background: var(--bg-primary);
          flex-wrap: wrap;
        }

        .back-button {
          padding: clamp(6px, 2vw, 8px) clamp(12px, 3vw, 16px);
          background: var(--accent);
          color: white;
          border: none;
          border-radius: clamp(4px, 1vw, 6px);
          cursor: pointer;
          font-size: clamp(12px, 2.5vw, 14px);
          white-space: nowrap;
        }

        .back-button:hover {
          background: #0056b3;
        }

        .chat-info h3 {
          margin: 0;
          color: var(--text-primary);
          font-size: clamp(16px, 3vw, 18px);
        }

        .chat-info p {
          margin: clamp(3px, 1vh, 5px) 0 0 0;
          color: var(--text-secondary);
          font-size: clamp(12px, 2.5vw, 14px);
        }

        .chat-controls {
          margin-left: auto;
        }

        .research-toggle {
          display: flex;
          align-items: center;
          gap: clamp(6px, 1.5vw, 8px);
          cursor: pointer;
          font-size: clamp(12px, 2.5vw, 14px);
          color: var(--text-secondary);
        }

        .research-toggle input[type="checkbox"] {
          width: clamp(14px, 3vw, 16px);
          height: clamp(14px, 3vw, 16px);
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
          padding: clamp(15px, 3vw, 20px);
          display: flex;
          flex-direction: column;
          gap: clamp(15px, 3vh, 20px);
        }

        .welcome-message {
          text-align: center;
          padding: clamp(40px, 15vh, 60px) clamp(15px, 5vw, 20px);
          color: var(--text-secondary);
        }

        .welcome-icon {
          font-size: clamp(32px, 10vw, 48px);
          margin-bottom: clamp(15px, 4vh, 20px);
        }

        .welcome-message h4 {
          margin: 0 0 clamp(8px, 2vh, 10px) 0;
          color: var(--text-primary);
          font-size: clamp(18px, 4vw, 20px);
        }

        .message {
          display: flex;
          flex-direction: column;
          gap: clamp(6px, 1.5vh, 8px);
          max-width: min(80%, 600px);
          width: 100%;
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
          gap: clamp(8px, 2vw, 10px);
        }

        .ai-avatar {
          width: clamp(28px, 6vw, 32px);
          height: clamp(28px, 6vw, 32px);
          border-radius: 50%;
          background: var(--accent);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: clamp(14px, 3vw, 16px);
        }

        .ai-name {
          font-weight: 600;
          color: var(--text-primary);
          font-size: clamp(14px, 2.5vw, 16px);
        }

        .message-content {
          padding: clamp(12px, 3vw, 16px);
          border-radius: clamp(8px, 2vw, 12px);
          background: var(--bg-primary);
          border: 1px solid var(--border-color);
          box-shadow: 0 2px 8px var(--shadow);
          word-wrap: break-word;
          overflow-wrap: break-word;
        }

        .user-message .message-content {
          background: var(--accent);
          color: white;
        }

        .answer-text {
          line-height: 1.6;
          font-size: clamp(14px, 2.5vw, 16px);
        }

        .loading-indicator {
          display: flex;
          flex-direction: column;
          gap: clamp(6px, 1.5vh, 8px);
        }

        .message-meta {
          font-size: clamp(10px, 2vw, 12px);
          color: var(--text-muted);
          padding: 0 clamp(3px, 1vw, 4px);
        }

        .user-message .message-meta {
          text-align: right;
        }

        .error-message {
          padding: 12px;
          background: rgba(220, 53, 69, 0.1);
          border: 1px solid var(--error);
          border-radius: 6px;
          color: var(--error);
          text-align: center;
        }

        .input-area {
          padding: clamp(15px, 3vw, 20px);
          border-top: 1px solid var(--border-color);
          background: var(--bg-primary);
        }

        .message-input-container {
          display: flex;
          gap: clamp(8px, 2vw, 12px);
          align-items: flex-end;
          max-width: 800px;
          margin: 0 auto;
        }

        .message-input-container textarea {
          flex: 1;
          padding: clamp(10px, 2.5vw, 12px);
          border: 2px solid var(--border-color);
          border-radius: clamp(6px, 1.5vw, 8px);
          background: var(--bg-primary);
          color: var(--text-primary);
          font-size: clamp(14px, 2.5vw, 16px);
          font-family: inherit;
          resize: vertical;
          min-height: clamp(40px, 8vh, 50px);
          max-height: 200px;
          box-sizing: border-box;
        }

        .message-input-container textarea:focus {
          outline: none;
          border-color: var(--accent);
        }

        .message-input-container textarea:disabled {
          background: var(--bg-tertiary);
          cursor: not-allowed;
        }

        .send-button {
          padding: clamp(10px, 2.5vw, 12px) clamp(14px, 3vw, 16px);
          background: var(--accent);
          color: white;
          border: none;
          border-radius: clamp(6px, 1.5vw, 8px);
          cursor: pointer;
          font-size: clamp(14px, 2.5vw, 16px);
          transition: all 0.2s ease;
          align-self: flex-start;
          white-space: nowrap;
          flex-shrink: 0;
        }

        .send-button:hover:not(:disabled) {
          background: #0056b3;
          transform: scale(1.05);
        }

        .send-button:disabled {
          background: var(--text-secondary);
          cursor: not-allowed;
        }

        .message-input-container {
          display: flex;
          gap: 12px;
          align-items: flex-end;
        }

        .message-input-container textarea {
          flex: 1;
          padding: 12px;
          border: 2px solid var(--border-color);
          border-radius: 8px;
          font-size: 16px;
          font-family: inherit;
          background: var(--bg-primary);
          color: var(--text-primary);
          resize: vertical;
          min-height: 50px;
          max-height: 200px;
        }

        .message-input-container textarea:focus {
          outline: none;
          border-color: var(--accent);
        }

        .message-input-container textarea:disabled {
          background: var(--bg-tertiary);
          cursor: not-allowed;
        }

        .send-button {
          padding: 12px 16px;
          background: var(--accent);
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-size: 16px;
          transition: background 0.2s ease;
        }

        .send-button:hover:not(:disabled) {
          background: #0056b3;
        }

        .send-button:disabled {
          background: var(--text-secondary);
          cursor: not-allowed;
        }

        /* Extra small screens (< 480px) */
        @media (max-width: 480px) {
          .chat-header {
            flex-direction: column;
            gap: 12px;
            align-items: stretch;
            padding: 12px;
          }

          .chat-controls {
            margin-left: 0;
            align-self: center;
          }

          .research-toggle {
            justify-content: center;
          }

          .messages-area {
            padding: 12px;
            gap: 12px;
          }

          .message {
            max-width: 100%;
          }

          .message-content {
            padding: 10px;
          }

          .input-area {
            padding: 12px;
          }

          .message-input-container {
            flex-direction: column;
            gap: 10px;
          }

          .message-input-container textarea {
            width: 100%;
            min-height: 80px;
          }

          .send-button {
            align-self: stretch;
            padding: 14px;
          }
        }

        /* Small screens (481px - 768px) */
        @media (min-width: 481px) and (max-width: 768px) {
          .chat-header {
            flex-wrap: wrap;
            gap: 15px;
            padding: 15px;
          }

          .chat-controls {
            margin-left: auto;
          }

          .messages-area {
            padding: 15px;
          }

          .message-input-container {
            max-width: none;
          }
        }

        /* Medium screens (769px - 1024px) */
        @media (min-width: 769px) and (max-width: 1024px) {
          .message-input-container {
            max-width: 700px;
          }
        }

        /* Large screens (1025px - 1440px) */
        @media (min-width: 1025px) and (max-width: 1440px) {
          .message-input-container {
            max-width: 800px;
          }
        }

        /* Extra large screens (> 1440px) */
        @media (min-width: 1441px) {
          .message-input-container {
            max-width: 1000px;
          }

          .chat-header {
            padding: 24px;
          }

          .messages-area {
            padding: 24px;
          }

          .input-area {
            padding: 24px;
          }
        }
      `}</style>
    </div>
  );
};

export default Chat;