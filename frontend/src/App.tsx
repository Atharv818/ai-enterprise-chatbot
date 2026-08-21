import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'
import { useState } from 'react'
import AppLayout from './components/AppLayout'
import DocumentUpload from './components/DocumentUpload'
import Chat from './components/Chat'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function Home() {
  const [, setUploadCount] = useState(0)

  return (
    <AppLayout>
      <div className="border-b border-gray-200 px-6 py-3">
        <DocumentUpload onUploadComplete={() => setUploadCount((c) => c + 1)} />
      </div>
      <Chat />
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
