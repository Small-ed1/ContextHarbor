import React, { useState, useRef, useCallback } from 'react';

const ChatMessageInput = ({ onSendMessage, placeholder = "Type your message..." }) => {
  const [content, setContent] = useState('');
  const editorRef = useRef(null);

  const handleInput = useCallback(() => {
    if (editorRef.current) {
      setContent(editorRef.current.innerHTML);
    }
  }, []);

  const handleKeyDown = useCallback((e) => {
    if (e.ctrlKey || e.metaKey) {
      switch (e.key) {
        case 'b':
          e.preventDefault();
          execCommand('bold');
          break;
        case 'i':
          e.preventDefault();
          execCommand('italic');
          break;
        case 'u':
          e.preventDefault();
          execCommand('underline');
          break;
        case 'k':
          e.preventDefault();
          insertLink();
          break;
        default:
          break;
      }
    }
  }, []);

  const handlePaste = useCallback((e) => {
    e.preventDefault();
    const text = e.clipboardData.getData('text/plain');
    document.execCommand('insertText', false, text);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const text = editorRef.current ? editorRef.current.textContent.trim() : '';
    if (text) {
      onSendMessage(text);
      if (editorRef.current) {
        editorRef.current.innerHTML = '';
      }
      setContent('');
    }
  };

  const execCommand = (command, value = null) => {
    document.execCommand(command, false, value);
    editorRef.current?.focus();
  };

  const isCommandActive = (command) => {
    return document.queryCommandState(command);
  };

  const insertCode = () => {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      const codeElement = document.createElement('code');
      codeElement.textContent = selection.toString() || 'code';
      range.deleteContents();
      range.insertNode(codeElement);
      setContent(editorRef.current.innerHTML);
    }
    editorRef.current?.focus();
  };

  const insertLink = () => {
    const url = prompt('Enter URL:');
    if (url) {
      execCommand('createLink', url);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="chat-input-form">
      <div className="rich-text-toolbar">
        <div className="toolbar-group">
          <button type="button" onClick={() => execCommand('bold')} title="Bold"><strong>B</strong></button>
          <button type="button" onClick={() => execCommand('italic')} title="Italic"><em>I</em></button>
          <button type="button" onClick={() => execCommand('underline')} title="Underline"><u>U</u></button>
        </div>
        <div className="toolbar-group">
          <button type="button" onClick={() => execCommand('formatBlock', 'h1')} title="Heading 1">H1</button>
          <button type="button" onClick={() => execCommand('formatBlock', 'h2')} title="Heading 2">H2</button>
          <button type="button" onClick={() => execCommand('formatBlock', 'blockquote')} title="Quote">"</button>
        </div>
        <div className="toolbar-group">
          <button type="button" onClick={insertCode} title="Code">` `</button>
          <button type="button" onClick={insertLink} title="Link">🔗</button>
        </div>
        <div className="toolbar-group">
          <button type="button" onClick={() => execCommand('insertUnorderedList')} title="Bullet List">•</button>
          <button type="button" onClick={() => execCommand('insertOrderedList')} title="Numbered List">1.</button>
        </div>
      </div>
      <div
        ref={editorRef}
        contentEditable
        className="rich-text-editor"
        onInput={handleInput}
        onKeyDown={handleKeyDown}
        onPaste={handlePaste}
        data-placeholder={placeholder}
        suppressContentEditableWarning={true}
      />
      <button type="submit" className="send-button">
        Send
      </button>
      <style jsx>{`
        .rich-text-toolbar {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-bottom: 8px;
          padding: 8px;
          background: var(--bg-secondary, #f8f9fa);
          border: 1px solid var(--border-color, #dee2e6);
          border-radius: 6px;
        }
        .toolbar-group {
          display: flex;
          gap: 2px;
          border-right: 1px solid var(--border-color, #dee2e6);
          padding-right: 8px;
        }
        .toolbar-group:last-child {
          border-right: none;
          padding-right: 0;
        }
        .rich-text-toolbar button {
          padding: 6px 10px;
          border: 1px solid var(--border-color, #dee2e6);
          background: var(--bg-primary, white);
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          color: var(--text-primary, #212529);
          transition: all 0.2s ease;
        }
        .rich-text-toolbar button:hover {
          background: var(--accent, #007bff);
          color: white;
          border-color: var(--accent, #007bff);
        }
        .rich-text-toolbar button:active {
          transform: scale(0.95);
        }
        .rich-text-editor {
          min-height: 80px;
          padding: 12px;
          border: 1px solid var(--border-color, #dee2e6);
          border-radius: 6px;
          outline: none;
          overflow-y: auto;
          background: var(--bg-primary, white);
          color: var(--text-primary, #212529);
          line-height: 1.5;
          font-family: inherit;
        }
        .rich-text-editor:focus {
          border-color: var(--accent, #007bff);
          box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }
        .rich-text-editor:empty:before {
          content: attr(data-placeholder);
          color: var(--text-secondary, #6c757d);
          pointer-events: none;
        }
        .send-button {
          margin-top: 12px;
          padding: 10px 20px;
          background: linear-gradient(135deg, var(--accent, #007bff), #0056b3);
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
          transition: all 0.2s ease;
        }
        .send-button:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
        }
        .send-button:active {
          transform: translateY(0);
        }
      `}</style>
    </form>
  );
};

export default ChatMessageInput;