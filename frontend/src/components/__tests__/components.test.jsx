import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Sidebar from '../Sidebar';
import ChatWindow from '../ChatWindow';

// Mock scrollToBottom behavior
window.HTMLElement.prototype.scrollIntoView = vi.fn();

describe('Sidebar Component', () => {
  it('renders correctly and displays sessions', () => {
    const mockSessions = [
      { id: '1', title: 'Session 1' },
      { id: '2', title: 'Session 2' }
    ];
    
    render(
      <Sidebar 
        sessions={mockSessions} 
        activeSessionId="1" 
        onSelectSession={vi.fn()} 
        onCreateSession={vi.fn()} 
      />
    );

    expect(screen.getByText('New Chat')).toBeInTheDocument();
    expect(screen.getByText('Session 1')).toBeInTheDocument();
    expect(screen.getByText('Session 2')).toBeInTheDocument();
  });
});

describe('ChatWindow Component', () => {
  it('displays empty state when there are no messages', () => {
    render(<ChatWindow messages={[]} onSendMessage={vi.fn()} onViewArtifact={vi.fn()} />);
    
    expect(screen.getByText('Welcome to Lenny Growth Assistant')).toBeInTheDocument();
  });

  it('renders messages correctly', () => {
    const messages = [
      { id: '1', role: 'user', content: 'Hello' },
      { id: '2', role: 'assistant', content: 'Hi there' }
    ];

    render(<ChatWindow messages={messages} onSendMessage={vi.fn()} onViewArtifact={vi.fn()} />);
    
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there')).toBeInTheDocument();
  });
});
