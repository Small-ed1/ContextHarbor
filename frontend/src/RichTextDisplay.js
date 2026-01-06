import React from 'react';

const RichTextDisplay = ({ content, className = '' }) => {
  // Convert markdown-like syntax to HTML
  const formatContent = (text) => {
    if (!text) return '';

    // Convert **bold** to <strong>
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Convert *italic* to <em>
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Convert `code` to <code>
    text = text.replace(/`(.*?)`/g, '<code>$1</code>');

    // Convert --- to <hr>
    text = text.replace(/^---$/gm, '<hr>');

    // Convert # ## ### to headings
    text = text.replace(/^### (.*$)/gm, '<h3>$1</h3>');
    text = text.replace(/^## (.*$)/gm, '<h2>$1</h2>');
    text = text.replace(/^# (.*$)/gm, '<h1>$1</h1>');

    // Convert - or * list items
    text = text.replace(/^- (.*$)/gm, '<li>$1</li>');
    text = text.replace(/^\* (.*$)/gm, '<li>$1</li>');

    // Wrap consecutive list items
    text = text.replace(/(<li>.*<\/li>\s*)+/g, '<ul>$&</ul>');

    // Convert numbered lists
    text = text.replace(/^\d+\. (.*$)/gm, '<li>$1</li>');
    // Wrap consecutive numbered list items
    text = text.replace(/(<li>.*<\/li>\s*)+/g, '<ol>$&</ol>');

    // Convert > blockquote
    text = text.replace(/^> (.*$)/gm, '<blockquote>$1</blockquote>');

    // Convert line breaks to <br> but avoid in code blocks
    text = text.replace(/\n/g, '<br>');

    return text;
  };

  const formattedContent = formatContent(content);

  return (
    <div
      className={`rich-text-display ${className}`}
      dangerouslySetInnerHTML={{ __html: formattedContent }}
    />
  );
};

export default RichTextDisplay;