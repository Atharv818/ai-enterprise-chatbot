import client from './client'

export interface AskResponse {
  question: string
  route: string
  answer: string
  conversation_id: string
  data: Record<string, unknown>[] | null
  sources: { text: string; document_id: string; chunk_index: number; score: number }[] | null
  generated_sql: string | null
  query_id: string | null
}

export async function askQuestion(question: string, conversationId?: string) {
  const response = await client.post<AskResponse>('/ask', {
    question,
    conversation_id: conversationId ?? null,
  })
  return response.data
}
