import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { register } from '../api/auth'
import { useAuth } from '../context/AuthContext'
import { APP_NAME, APP_TAGLINE } from '../config/brand'

const SHOW_GOOGLE = false // flip to true once Google OAuth exists on the backend

function Logo({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true" className="text-terracotta">
      <g stroke="currentColor" strokeWidth="3" strokeLinecap="round">
        {[0, 30, 60, 90, 120, 150].map((deg) => (
          <line key={deg} x1="16" y1="3" x2="16" y2="29" transform={`rotate(${deg} 16 16)`} />
        ))}
      </g>
    </svg>
  )
}

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.6l6.8-6.8C35.8 2.4 30.3 0 24 0 14.6 0 6.5 5.4 2.6 13.3l7.9 6.1C12.4 13.6 17.7 9.5 24 9.5z" />
      <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.7c-.6 3-2.3 5.5-4.8 7.2l7.6 5.9c4.4-4.1 7-10.1 7-17.6z" />
      <path fill="#FBBC05" d="M10.5 28.6A14.5 14.5 0 0 1 9.5 24c0-1.6.3-3.2.8-4.6l-7.9-6.1A24 24 0 0 0 0 24c0 3.9.9 7.5 2.6 10.7l7.9-6.1z" />
      <path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.6-5.9c-2.1 1.4-4.9 2.3-8.3 2.3-6.3 0-11.6-4.1-13.5-9.9l-7.9 6.1C6.5 42.6 14.6 48 24 48z" />
    </svg>
  )
}

function MailIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="m3 7 9 6 9-6" />
    </svg>
  )
}

function Blob() {
  return (
    <svg
      className="pointer-events-none absolute -right-16 -top-10 hidden h-[380px] w-[380px] md:block"
      viewBox="0 0 400 400"
      aria-hidden="true"
    >
      <path
        d="M60 40 C150 -10 300 0 360 70 C410 130 380 230 330 280 C290 320 230 330 180 300 C140 280 110 300 80 270 C30 220 -10 100 60 40Z"
        fill="#D97757"
      />
      <g stroke="#F6D9CC" strokeWidth="2" fill="#F6D9CC">
        <line x1="190" y1="90" x2="260" y2="130" />
        <line x1="260" y1="130" x2="320" y2="90" />
        <line x1="260" y1="130" x2="300" y2="200" />
        <line x1="190" y1="90" x2="150" y2="160" />
        <circle cx="190" cy="90" r="9" />
        <circle cx="260" cy="130" r="7" />
        <circle cx="320" cy="90" r="6" />
        <circle cx="300" cy="200" r="8" />
        <circle cx="150" cy="160" r="5" />
      </g>
    </svg>
  )
}

export default function Register() {
  const [showEmailForm, setShowEmailForm] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [tenantName, setTenantName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const auth = useAuth()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await register(email, password, tenantName)
      auth.login(data.access_token)
      navigate('/')
    } catch {
      setError('Something went wrong creating your account. Try again.')
    } finally {
      setLoading(false)
    }
  }

  const btn =
    'w-full flex items-center justify-center gap-3 rounded-xl border border-cream-dark bg-white px-4 py-3 text-[15px] font-medium text-warm-black transition hover:bg-cream/60 disabled:opacity-60'

  const input =
    'w-full rounded-xl border border-cream-dark bg-white px-4 py-3 text-[15px] text-warm-black outline-none transition focus:border-terracotta focus:ring-2 focus:ring-terracotta/20'

  return (
    <div className="relative min-h-screen overflow-hidden bg-cream">
      {/* Top-left brand */}
      <div className="absolute left-6 top-6 flex items-center gap-2 sm:left-10 sm:top-8">
        <Logo />
        <span className="font-serif text-2xl font-medium text-warm-black">{APP_NAME}</span>
      </div>

      <Blob />

      <main className="relative z-10 flex min-h-screen items-center justify-center px-4 py-24">
        <div className="w-full max-w-[440px] rounded-3xl border border-cream-dark bg-white/60 px-8 py-10 shadow-[0_10px_40px_-12px_rgba(60,50,30,0.15)] sm:px-10">
          <div className="mb-8 flex flex-col items-center">
            <div className="flex items-center gap-2">
              <Logo size={32} />
              <span className="font-serif text-[32px] font-medium text-warm-black">{APP_NAME}</span>
            </div>
            <p className="mt-1 text-sm text-warm-gray">{APP_TAGLINE}</p>
          </div>

          <h1 className="text-center font-serif text-2xl text-warm-black">
            {showEmailForm ? 'Create your account' : `Get started with ${APP_NAME}`}
          </h1>
          <p className="mb-8 mt-2 text-center text-sm text-warm-gray">
            {showEmailForm
              ? 'Start asking questions about your data'
              : 'Sign in or create an account to continue'}
          </p>

          {!showEmailForm ? (
            <div className="space-y-3">
              {SHOW_GOOGLE && (
                <button type="button" className={btn}>
                  <GoogleIcon />
                  Continue with Google
                </button>
              )}
              <button type="button" className={btn} onClick={() => setShowEmailForm(true)}>
                <MailIcon />
                Sign up with email
              </button>

              <div className="flex items-center gap-4 pt-3">
                <div className="h-px flex-1 bg-cream-dark" />
                <span className="text-xs text-warm-gray">or</span>
                <div className="h-px flex-1 bg-cream-dark" />
              </div>

              <p className="pt-2 text-center text-sm text-warm-gray">
                Already have an account?{' '}
                <Link to="/login" className="font-medium text-terracotta underline">
                  Log in
                </Link>
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-3">
              <input
                type="text"
                value={tenantName}
                onChange={(e) => setTenantName(e.target.value)}
                required
                autoFocus
                autoComplete="organization"
                className={input}
                placeholder="Company name (e.g. Acme Corp)"
              />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                className={input}
                placeholder="you@company.com"
              />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                autoComplete="new-password"
                className={input}
                placeholder="Password (at least 8 characters)"
              />

              {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-xl bg-terracotta px-4 py-3 text-[15px] font-medium text-white transition hover:bg-terracotta-dark disabled:opacity-50"
              >
                {loading ? 'Creating account...' : 'Create account'}
              </button>

              <button
                type="button"
                onClick={() => {
                  setShowEmailForm(false)
                  setError('')
                }}
                className="w-full pt-1 text-center text-sm text-warm-gray hover:text-warm-black"
              >
                ← Back to all options
              </button>
            </form>
          )}

          <p className="mt-8 text-center text-xs leading-relaxed text-warm-gray">
            By continuing, you agree to {APP_NAME}'s{' '}
            <a href="#" className="underline hover:text-warm-black">Terms of Service</a> and{' '}
            <a href="#" className="underline hover:text-warm-black">Privacy Policy</a>.
          </p>
        </div>
      </main>
    </div>
  )
}