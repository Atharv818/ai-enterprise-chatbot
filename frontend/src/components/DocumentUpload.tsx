import { useState, useRef } from 'react'
import { uploadDocument } from '../api/documents'

interface DocumentUploadProps {
  onUploadComplete: () => void
}

export default function DocumentUpload({ onUploadComplete }: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [status, setStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setStatus(null)

    try {
      const result = await uploadDocument(file)
      if (result.status === 'ready') {
        setStatus({ type: 'success', message: `${result.filename} uploaded and ready.` })
        onUploadComplete()
      } else {
        setStatus({ type: 'error', message: `${result.filename} failed to process.` })
      }
    } catch {
      setStatus({ type: 'error', message: "Couldn't upload that file. Try again." })
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  return (
    <div className="flex flex-col items-start gap-2">
      <input
        ref={fileInputRef}
        type="file"
        accept=".xlsx,.csv,.pdf,.docx,.txt"
        onChange={handleFileChange}
        className="hidden"
        id="file-upload"
      />
      <label
        htmlFor="file-upload"
        className={`cursor-pointer text-sm rounded-lg border border-gray-200 px-3 py-2 hover:bg-gray-50 ${
          uploading ? 'opacity-50 pointer-events-none' : ''
        }`}
      >
        {uploading ? 'Uploading...' : '+ Upload document'}
      </label>

      {status && (
        <p className={`text-sm ${status.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
          {status.message}
        </p>
      )}
    </div>
  )
}