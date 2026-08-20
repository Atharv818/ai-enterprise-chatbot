import client from './client'

export interface DocumentResponse {
  id: string
  filename: string
  file_type: string
  status: string
  uploaded_at: string
}

export async function uploadDocument(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await client.post<DocumentResponse>('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}
