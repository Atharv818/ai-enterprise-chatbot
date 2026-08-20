import { type ReactNode } from 'react'
import { useAuth } from '../context/AuthContext'

export default function AppLayout({ children }: { children: ReactNode }) {
  const { logout } = useAuth()

  return (
    <div className="min-h-screen flex bg-gray-50">
      <aside className="w-56 bg-white border-r border-gray-200 flex flex-col p-3">
        <div className="flex items-center gap-2 px-1 py-2 mb-4">
          <div className="w-6 h-6 rounded-md bg-gray-900 flex items-center justify-center">
            <span className="text-white text-xs font-medium">A</span>
          </div>
          <span className="text-sm font-medium text-gray-900">Enterprise AI</span>
        </div>

        <button className="w-full flex items-center gap-2 text-sm rounded-lg border border-gray-200 px-3 py-2 mb-4 hover:bg-gray-50">
          <span>+</span> New conversation
        </button>

        <div className="flex-1">
          <p className="text-xs text-gray-400 px-2 mb-1">Recent</p>
          <p className="text-xs text-gray-400 px-2">No conversations yet</p>
        </div>

        <button
          onClick={logout}
          className="text-sm text-gray-500 hover:text-gray-900 text-left px-2 py-2 border-t border-gray-200 mt-2"
        >
          Log out
        </button>
      </aside>

      <main className="flex-1 flex flex-col">{children}</main>
    </div>
  )
}

