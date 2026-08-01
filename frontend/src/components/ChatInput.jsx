import React, { useState } from 'react';
import { Send } from 'lucide-react';

export default function ChatInput({ onSendMessage }) {
  const [text, setText] = useState('');

  const handleSend = () => {
    if (text.trim()) {
      onSendMessage(text.trim());
      setText('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="input-area">
      <div className="chat-input-wrapper">
        <textarea
          className="chat-input"
          placeholder="Ask about product market fit, or request a dashboard component..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          style={{ minHeight: '24px', maxHeight: '120px' }}
        />
        <button className="send-btn" onClick={handleSend} disabled={!text.trim()} title="Send Message">
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
