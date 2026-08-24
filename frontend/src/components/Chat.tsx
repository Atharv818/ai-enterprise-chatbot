import { useState, useEffect, useRef } from 'react'
import { askQuestion, type AskResponse } from '../api/ask'
import { getConversation } from '../api/conversations'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import ReactMarkdown from 'react-markdown'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  response?: AskResponse
}

interface ChatProps {
  conversationId?: string
  onConversationChange: (id: string) => void
}

export default function Chat({ conversationId, onConversationChange }: ChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()
  const { logout } = useAuth()

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  useEffect(() => {
    if (!conversationId) {
      setMessages([])
      return
    }
    setLoadingHistory(true)
    getConversation(conversationId)
      .then((detail) => {
        setMessages(
          detail.messages.map((m) => {
            const parsedData = m.data ? JSON.parse(m.data) : null
            return {
              role: m.role as 'user' | 'assistant',
              content: m.content,
              response:
                m.role === 'assistant'
                  ? ({
                      question: '',
                      route: m.route ?? '',
                      answer: m.content,
                      conversation_id: conversationId,
                      data: parsedData,
                      sources: null,
                      generated_sql: null,
                      query_id: m.query_id,
                    } as AskResponse)
                  : undefined,
            }
          })
        )
      })
      .catch(() => setMessages([]))
      .finally(() => setLoadingHistory(false))
  }, [conversationId])

  async function handleSend(e: React.FormEvent) {
    e.preventDefault()
    if (!input.trim() || loading) return

    const question = input.trim()
    setMessages((prev) => [...prev, { role: 'user', content: question }])
    setInput('')
    setLoading(true)

    try {
      const response = await askQuestion(question, conversationId)
      onConversationChange(response.conversation_id)
      setMessages((prev) => [...prev, { role: 'assistant', content: response.answer, response }])
    } catch (err) {
      let message = "Something went wrong answering that. Try again."
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { status?: number } }
        if (axiosErr.response?.status === 429) {
          message = "You're asking questions a bit too fast. Wait a moment and try again."
        } else if (axiosErr.response?.status === 401) {
          message = "Your session expired. Redirecting to login..."
          logout()
          setTimeout(() => navigate('/login'), 1500)
        }
      }
      setMessages((prev) => [...prev, { role: 'assistant', content: message }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <div className="flex-1 overflow-y-auto min-h-0">
        <div className="max-w-3xl w-full mx-auto px-6 py-6 space-y-4">
          {loadingHistory && <p className="text-warm-gray text-center mt-20">Loading conversation...</p>}

          {!loadingHistory && messages.length === 0 && (
            <div className="text-center mt-20">
              <div className="w-12 h-12 bg-terracotta rounded-xl flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-lg font-medium">A</span>
              </div>
              <h2 className="text-lg font-medium text-warm-black mb-1">Ask anything about your data</h2>
              <p className="text-warm-gray text-sm">
                Upload a spreadsheet or document above, then ask a question to get started.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[75%] rounded-xl px-4 py-2 text-sm ${
                  msg.role === 'user'
                    ? 'bg-peach text-warm-black'
                    : 'bg-white border border-cream-dark'
                }`}
              >
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>

                {msg.response?.data && msg.response.data.length > 0 && (
                  <div className="mt-2 overflow-x-auto">
                    <table className="text-xs border-collapse">
                      <thead>
                        <tr>
                          {Object.keys(msg.response.data[0]).map((key) => (
                            <th
                              key={key}
                              className="border-b border-gray-200 px-2 py-1 text-left text-gray-500"
                            >
                              {key}
                            </th>
                          ))}
                        </tr>
                      </thead>

                      <tbody>
                        {msg.response.data.map((row, ri) => (
                          <tr key={ri}>
                            {Object.values(row).map((val, vi) => (
                              <td
                                key={vi}
                                className="border-b border-gray-100 px-2 py-1"
                              >
                                {String(val)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {msg.response?.query_id &&
                  msg.response?.data &&
                  msg.response.data.length >= 10 && (
                    <a
                      href={`/api/query/export/${msg.response.query_id}`}
                      className="inline-block mt-2 text-xs text-blue-600 underline"
                    >
                      Download CSV
                    </a>
                  )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-1.5 text-sm text-warm-gray">
                <span className="w-1.5 h-1.5 bg-warm-gray rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                <span className="w-1.5 h-1.5 bg-warm-gray rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span className="w-1.5 h-1.5 bg-warm-gray rounded-full animate-bounce"></span>
            </div>
           )}
           <div ref={messagesEndRef} />     
        </div>
      </div>

      <form
        onSubmit={handleSend}
        className="flex gap-2 border border-cream-dark rounded-xl p-2 bg-white max-w-3xl w-[calc(100%-3rem)] mx-auto mb-6"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your data"
          className="flex-1 px-2 py-1 text-sm focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-terracotta text-white text-sm rounded-lg px-4 py-1.5 hover:bg-terracotta-dark disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  )
}