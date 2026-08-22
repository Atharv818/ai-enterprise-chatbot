import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login } from '../api/auth'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const auth = useAuth()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await login(email, password)
      auth.login(data.access_token)
      navigate('/')
    } catch {
      setError("That email or password isn't right. Try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-cream flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <h1 className="text-2xl font-semibold text-warm-black mb-1">Welcome back</h1>
        <p className="text-warm-gray mb-8">Log in to your account</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-warm-black mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-lg border border-cream-dark px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-terracotta"
              placeholder="you@company.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-warm-black mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-lg border border-cream-dark px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-terracotta"
              placeholder="••••••••"
            />
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-terracotta text-white rounded-lg py-2 font-medium hover:bg-terracotta-dark disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Log in'}
          </button>
        </form>

        <p className="text-sm text-warm-gray mt-6 text-center">
          Don't have an account?{' '}
          <Link to="/register" className="text-terracotta font-medium">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}