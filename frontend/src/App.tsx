import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'
import AppLayout from './components/AppLayout'
import DocumentUpload from './components/DocumentUpload'
import Chat from './components/Chat'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function Home() {
  const [conversationId, setConversationId] = useState<string | undefined>()
  const [refreshKey, setRefreshKey] = useState(0)

  function handleConversationChange(id: string) {
    setConversationId(id)
    setRefreshKey((k) => k + 1)
  }

  function handleNewConversation() {
    setConversationId(undefined)
  }

  return (
    <AppLayout
      activeConversationId={conversationId}
      onSelectConversation={setConversationId}
      onNewConversation={handleNewConversation}
      refreshKey={refreshKey}
    >
      <div className="border-b border-cream-dark px-6 py-3">
        <DocumentUpload onUploadComplete={() => setRefreshKey((k) => k + 1)} />
      </div>
      <Chat conversationId={conversationId} onConversationChange={handleConversationChange} />
    </AppLayout>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App