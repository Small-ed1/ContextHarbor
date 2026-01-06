import React, { useState, useEffect } from 'react';
import React, { useState, useEffect } from 'react';

function HomePage({ onStartChat, onStartResearch, selectedModel, onModelChange, settings }) {
  const [scrollY, setScrollY] = useState(0);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSendMessage = () => {
    if (message.trim()) {
      onStartChat(message.trim());
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const features = [
    {
      icon: '💬',
      title: 'Intelligent Chat',
      description: 'Have natural conversations with AI models. Ask questions, get explanations, and explore ideas.'
    },
    {
      icon: '🔬',
      title: 'Deep Research',
      description: 'Conduct comprehensive research with multi-agent systems. Get detailed analysis and insights.'
    },
    {
      icon: '📚',
      title: 'Document Q&A',
      description: 'Upload documents and ask questions about their content. Perfect for research papers and manuals.'
    },
    {
      icon: '📊',
      title: 'Agent Dashboard',
      description: 'Monitor and manage your AI agents in real-time. See their progress and performance.'
    },
    {
      icon: '⚙️',
      title: 'Advanced Settings',
      description: 'Customize your experience with theme preferences, model selection, and advanced options.'
    }
  ];

  return (
    <div className="home-page">
      <h1>Welcome to Router Phase 1</h1>
      <button onClick={() => onStartChat("Hello!")}>Start Chat</button>
      <button onClick={onStartResearch}>Deep Research</button>
    </div>
  );
};

export default HomePage;