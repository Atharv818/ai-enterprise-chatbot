import client from './client'

export interface ConversationSummary {
  id: string
  created_at: string
  last_message: string | null
  message_count: number
}

export interface Message {
  id: string
  role: string
  content: string
  route: string | null
  data: string | null
  query_id: string | null
  created_at: string
}

export interface ConversationDetail {
  id: string
  created_at: string
  messages: Message[]
}

export async function listConversations() {
  const response = await client.get<ConversationSummary[]>('/conversations')
  return response.data
}

export async function getConversation(id: string) {
  const response = await client.get<ConversationDetail>(`/conversations/${id}`)
  return response.data
}

export async function deleteConversation(id: string) {
  await client.delete(`/conversations/${id}`)
}