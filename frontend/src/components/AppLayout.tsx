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
    <div className="h-screen flex bg-cream overflow-hidden">
      <aside className="w-56 bg-cream border-r border-cream-dark flex flex-col p-3 overflow-y-auto">
        <div className="flex items-center gap-2 px-1 py-2 mb-4">
          <div className="w-6 h-6 rounded-md bg-terracotta flex items-center justify-center">
            <span className="text-white text-xs font-medium">A</span>
          </div>
          <span className="text-sm font-medium text-warm-black">Enterprise AI</span>
        </div>

        <button
          onClick={onNewConversation}
          className="w-full flex items-center gap-2 text-sm rounded-lg border border-terracotta text-terracotta px-3 py-2 mb-4 hover:bg-peach"
        >
          <span>+</span> New conversation
        </button>

        <div className="flex-1 overflow-y-auto">
          <p className="text-xs text-warm-gray px-2 mb-1">Recent</p>

          {loadingList && <p className="text-xs text-warm-gray px-2">Loading...</p>}

          {!loadingList && conversations.length === 0 && (
            <p className="text-xs text-warm-gray px-2">No conversations yet</p>
          )}

          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => onSelectConversation(conv.id)}
              className={`w-full text-left text-xs px-2 py-2 rounded-lg truncate ${
                conv.id === activeConversationId
                  ? 'bg-peach text-warm-black'
                  : 'text-warm-gray hover:bg-cream-dark'
              }`}
            >
              {conv.last_message || 'New conversation'}
            </button>
          ))}
        </div>

        <button
          onClick={logout}
          className="text-sm text-warm-gray hover:text-warm-black text-left px-2 py-2 border-t border-cream-dark mt-2"
        >
          Log out
        </button>
      </aside>

      <main className="flex-1 flex flex-col overflow-hidden min-h-0 bg-white">{children}</main>
    </div>
  )
}