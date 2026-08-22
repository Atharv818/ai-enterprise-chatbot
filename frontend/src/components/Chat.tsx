import { useState } from 'react'
import { askQuestion, type AskResponse } from '../api/ask'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  response?: AskResponse
}

export default function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | undefined>()

  async function handleSend(e: React.FormEvent) {
    e.preventDefault()
    if (!input.trim() || loading) return

    const question = input.trim()
    setMessages((prev) => [...prev, { role: 'user', content: question }])
    setInput('')
    setLoading(true)

    try {
      const response = await askQuestion(question, conversationId)
      setConversationId(response.conversation_id)
      setMessages((prev) => [...prev, { role: 'assistant', content: response.answer, response }])
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: "Something went wrong answering that. Try again." },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <div className="flex-1 overflow-y-auto min-h-0">
        <div className="max-w-3xl w-full mx-auto px-6 py-6 space-y-4">
          {messages.length === 0 && (
            <p className="text-warm-gray text-center mt-20">
              Ask a question about your uploaded data.
            </p>
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
                <p>{msg.content}</p>

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

          {loading && <p className="text-sm text-gray-400">Thinking...</p>}
        </div>
      </div>

      <form
        onSubmit={handleSend}
        className="flex gap-2 border border-cream-dark rounded-xl p-2 bg-white max-w-3xl w-full mx-auto"
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