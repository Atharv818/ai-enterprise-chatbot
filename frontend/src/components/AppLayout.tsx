// frontend/src/components/AppLayout.tsx
import { type ReactNode, useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { listConversations, type ConversationSummary } from '../api/conversations'
import { APP_NAME, APP_SIDEBAR_SUBTITLE } from '../config/brand'
import Logo from './Logo'

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
    <div className="h-screen flex bg-[#F1F3EA] overflow-hidden">
      <aside className="w-56 bg-[#F1F3EA] border-r border-[#E1E6D8] flex flex-col p-3 overflow-y-auto">
        <div className="flex items-center gap-2 px-1 py-2 mb-4">
          <Logo size={32} />
          <div className="min-w-0">
            <p className="text-sm font-medium text-warm-black leading-tight truncate">{APP_NAME}</p>
            <p className="text-[11px] text-warm-gray leading-tight truncate">{APP_SIDEBAR_SUBTITLE}</p>
          </div>
        </div>

        <button
          onClick={onNewConversation}
          className="w-full flex items-center gap-2 text-sm rounded-lg border border-[#2A9A40] text-[#2A9A40] px-3 py-2 mb-4 hover:bg-[#E3F2E0] transition-colors"
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
                    ? 'bg-[#E3F2E0] text-warm-black border-[#2A9A40] font-medium'
                    : 'text-warm-gray hover:bg-[#E8EEDF] border-transparent'
                }`}
              >
                {conv.last_message || 'New conversation'}
              </button>
            )
          })}
        </div>

        <button
          onClick={logout}
          className="text-sm text-warm-gray hover:text-warm-black text-left px-2 py-2 border-t border-[#E1E6D8] mt-2"
        >
          Log out
        </button>
      </aside>

      <main className="flex-1 flex flex-col overflow-hidden min-h-0 bg-[#F7F8F2]">{children}</main>
    </div>
  )
}