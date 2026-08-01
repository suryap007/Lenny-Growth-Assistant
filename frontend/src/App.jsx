import { useState, useEffect, useRef } from 'react'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'
import ArtifactViewer from './components/ArtifactViewer'

const API_BASE = 'http://localhost:8000/api'

function App() {
  const [sessions, setSessions] = useState([])
  const [activeSessionId, setActiveSessionId] = useState(null)
  const activeSessionIdRef = useRef(null)
  const [messages, setMessages] = useState([])
  const [activeArtifact, setActiveArtifact] = useState(null)
  const [config, setConfig] = useState({})
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000)
      return () => clearTimeout(timer)
    }
  }, [error])

  useEffect(() => {
    activeSessionIdRef.current = activeSessionId
  }, [activeSessionId])

  useEffect(() => {
    fetchConfig()
    fetchSessions()
  }, [])

  const fetchConfig = async () => {
    try {
      const res = await fetch(`${API_BASE}/config`)
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      setConfig(await res.json())
    } catch (e) {
      console.error(e)
      setError("Failed to fetch configuration.")
    }
  }

  const fetchSessions = async () => {
    try {
      const res = await fetch(`${API_BASE}/sessions`)
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      setSessions(data)
      if (data.length > 0 && !activeSessionId) {
        handleSelectSession(data[0].id)
      }
    } catch (e) {
      console.error(e)
      setError("Failed to load chat sessions.")
    }
  }

  const handleCreateSession = async () => {
    try {
      const res = await fetch(`${API_BASE}/sessions`, { method: 'POST' })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const newSession = await res.json()
      setSessions([newSession, ...sessions])
      setActiveSessionId(newSession.id)
      setMessages([])
      setActiveArtifact(null)
    } catch (e) {
      console.error(e)
      setError("Failed to create a new session.")
    }
  }

  const handleSelectSession = async (id) => {
    setActiveSessionId(id)
    setActiveArtifact(null)
    try {
      const res = await fetch(`${API_BASE}/sessions/${id}`)
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      setMessages(data.messages || [])
    } catch (e) {
      console.error(e)
      setError("Failed to load session details.")
    }
  }

  const handleSendMessage = async (text) => {
    let currentSessionId = activeSessionId
    if (!currentSessionId) {
      // Auto-create if no session
      try {
        const res = await fetch(`${API_BASE}/sessions`, { method: 'POST' })
        if (!res.ok) throw new Error("Failed to auto-create session")
        const newSession = await res.json()
        setSessions([newSession, ...sessions])
        currentSessionId = newSession.id
        setActiveSessionId(currentSessionId)
      } catch (e) { 
        console.error(e)
        setError("Failed to create a session to send the message.")
        return 
      }
    }

    const tempMsg = { id: Date.now(), role: 'user', content: text }
    setMessages(prev => [...prev, tempMsg])

    try {
      setIsLoading(true)
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: currentSessionId, message: text })
      })
      
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || `Server error: ${res.status}`)
      }
      
      const data = await res.json()
      const assistantMsg = { 
        id: Date.now() + 1, 
        role: 'assistant', 
        content: data.answer,
        artifact_type: data.artifact?.artifact_type,
        artifact_content: data.artifact?.artifact_content
      }
      
      if (activeSessionIdRef.current === currentSessionId) {
        setMessages(prev => [...prev, assistantMsg])
        if (data.artifact) {
          setActiveArtifact(data.artifact)
        }
      }
      // Refresh sessions to get updated title
      fetchSessions()
    } catch (e) {
      console.error(e)
      setError(e.message || "An error occurred while sending the message.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app-container">
      {error && (
        <div className="toast-notification">
          <span>{error}</span>
          <button className="toast-close-btn" onClick={() => setError(null)}>×</button>
        </div>
      )}
      <Sidebar 
        sessions={sessions} 
        activeSessionId={activeSessionId} 
        onSelectSession={handleSelectSession}
        onCreateSession={handleCreateSession}
      />
      
      <main className="main-content">
        <header className="top-bar">
          <h2>Lenny Growth Assistant</h2>
          <div className="provider-badge">
            Provider: {config.llm_provider || 'Loading...'}
          </div>
        </header>

        <div className="workspace">
          <ChatWindow 
            messages={messages} 
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            onViewArtifact={(msg) => setActiveArtifact({
              artifact_type: msg.artifact_type,
              artifact_title: 'View Artifact',
              artifact_content: msg.artifact_content
            })}
          />
          
          {activeArtifact && (
            <ArtifactViewer 
              artifact={activeArtifact} 
              onClose={() => setActiveArtifact(null)} 
            />
          )}
        </div>
      </main>
    </div>
  )
}

export default App
