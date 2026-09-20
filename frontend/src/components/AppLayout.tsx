import { type ReactNode, useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { listConversations, type ConversationSummary } from '../api/conversations'

interface AppLayoutProps {
  children: ReactNode
  activeConversationId?: string
  onSelectConversation: (id: string) => void
  onNewConversation: () => void
  refreshKey?: number
}

export default function AppLayout({
  children,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  refreshKey,
}: AppLayoutProps) {
  const { logout } = useAuth()
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [loadingList, setLoadingList] = useState(true)

  useEffect(() => {
    listConversations()
      .then(setConversations)
      .catch(() => setConversations([]))
      .finally(() => setLoadingList(false))
  }, [refreshKey])

  return (
    <div className="h-screen flex bg-sidebar-bg overflow-hidden">
      <aside className="w-56 bg-sidebar-bg border-r border-card-border flex flex-col p-3 overflow-y-auto">
        <div className="flex items-center gap-2 px-1 py-2 mb-4">
          <div className="w-7 h-7 rounded-md bg-terracotta flex items-center justify-center shrink-0">
            <span className="text-white text-xs font-medium">A</span>
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-warm-black leading-tight truncate">Enterprise AI</p>
            <p className="text-[11px] text-warm-gray leading-tight truncate">Ask your company data</p>
          </div>
        </div>

        <button
          onClick={onNewConversation}
          className="w-full flex items-center gap-2 text-sm rounded-lg border border-terracotta text-terracotta px-3 py-2 mb-4 hover:bg-peach transition-colors"
        >
          <span>+</span> New conversation
        </button>

        <div className="flex-1 overflow-y-auto">
          <p className="text-xs text-warm-gray px-2 mb-1">Recent</p>

          {loadingList && <p className="text-xs text-warm-gray px-2">Loading...</p>}

          {!loadingList && conversations.length === 0 && (
            <p className="text-xs text-warm-gray px-2">No conversations yet</p>
          )}

          {conversations.map((conv) => {
            const isActive = conv.id === activeConversationId
            return (
              <button
                key={conv.id}
                onClick={() => onSelectConversation(conv.id)}
                className={`w-full text-left text-xs px-2.5 py-2 rounded-lg truncate mb-0.5 border-l-[3px] transition-colors ${
                  isActive
                    ? 'bg-peach text-warm-black border-terracotta font-medium'
                    : 'text-warm-gray hover:bg-cream-dark border-transparent'
                }`}
              >
                {conv.last_message || 'New conversation'}
              </button>
            )
          })}
        </div>

        <button
          onClick={logout}
          className="text-sm text-warm-gray hover:text-warm-black text-left px-2 py-2 border-t border-card-border mt-2"
        >
          Log out
        </button>
      </aside>

      <main className="flex-1 flex flex-col overflow-hidden min-h-0 bg-main-bg">{children}</main>
    </div>
  )
}