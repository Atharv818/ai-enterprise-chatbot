import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'
import { useState } from 'react'
import AppLayout from './components/AppLayout'
import DocumentUpload from './components/DocumentUpload'


function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function Home() {
  const [uploadCount, setUploadCount] = useState(0)

  return (
    <AppLayout>
      <div className="flex-1 flex flex-col items-center justify-center gap-4">
        <p className="text-gray-400">Chat UI comes next.</p>
        <DocumentUpload onUploadComplete={() => setUploadCount((c) => c + 1)} />
        {uploadCount > 0 && (
          <p className="text-sm text-gray-500">{uploadCount} document(s) uploaded this session.</p>
        )}
      </div>
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
