import axios from 'axios'
import client from './client'

export interface DocumentResponse {
  id: string
  filename: string
  file_type: string
  status: string
  uploaded_at: string
}

export interface DuplicateDocumentInfo {
  message: string
  document_id: string
  filename: string
  uploaded_at: string
  status: string
  can_reprocess: boolean
  reprocess_recommended: boolean
}

export async function uploadDocument(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await client.post<DocumentResponse>('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function reprocessDocument(documentId: string) {
  const response = await client.post<DocumentResponse>(`/documents/${documentId}/reprocess`)
  return response.data
}

export function getDuplicateInfo(error: unknown): DuplicateDocumentInfo | null {
  if (axios.isAxiosError(error) && error.response?.status === 409) {
    // FastAPI's HTTPException(detail=...) wraps the payload under "detail"
    return error.response.data?.detail as DuplicateDocumentInfo
  }
  return null
}