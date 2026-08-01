import React from 'react';
import MarkdownRenderer from './MarkdownRenderer';
import { Bot, User, Code2 } from 'lucide-react';

export default function MessageBubble({ message, onViewArtifact }) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`message-bubble-wrapper ${isUser ? 'user' : 'assistant'}`}>
      <div className={`avatar ${isUser ? 'user' : 'assistant'}`}>
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </div>
      <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
        <div className="message-content">
          <MarkdownRenderer content={message.content} />
        </div>
        
        {message.artifact_type && (
          <button className="view-artifact-btn" onClick={onViewArtifact}>
            <Code2 size={16} />
            View {message.artifact_type.toUpperCase()} Artifact
          </button>
        )}
      </div>
    </div>
  );
}
