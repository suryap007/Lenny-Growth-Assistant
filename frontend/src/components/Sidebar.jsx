import React from 'react';
import { Plus, MessageSquare } from 'lucide-react';

export default function Sidebar({ sessions, activeSessionId, onSelectSession, onCreateSession }) {
  return (
    <aside className="sidebar">
      <button className="new-chat-btn" onClick={onCreateSession}>
        <Plus size={18} />
        New Chat
      </button>
      <div className="session-list">
        {sessions.map(session => (
          <div 
            key={session.id} 
            className={`session-item ${session.id === activeSessionId ? 'active' : ''}`}
            onClick={() => onSelectSession(session.id)}
            title={session.title || 'New Chat'}
          >
            <MessageSquare size={16} />
            {session.title || 'New Chat'}
          </div>
        ))}
      </div>
    </aside>
  );
}
