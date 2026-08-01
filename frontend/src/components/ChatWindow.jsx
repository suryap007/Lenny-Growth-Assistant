import React, { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import { Sparkles } from 'lucide-react';

export default function ChatWindow({ messages, isLoading, onSendMessage, onViewArtifact }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="chat-window">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <Sparkles className="empty-state-icon" />
            <h3>Welcome to Lenny Growth Assistant</h3>
            <p>Ask a question about growth, product management, or request an artifact!</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <MessageBubble 
              key={msg.id || idx} 
              message={msg} 
              onViewArtifact={() => onViewArtifact(msg)} 
            />
          ))
        )}
        {isLoading && (
          <div className="message-bubble-wrapper assistant">
            <div className="avatar assistant">
              <Sparkles size={20} />
            </div>
            <div className="message-bubble assistant loading-indicator">
              <div className="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSendMessage={onSendMessage} />
    </div>
  );
}
