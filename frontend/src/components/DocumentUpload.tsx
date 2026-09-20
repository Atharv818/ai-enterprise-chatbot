import { useState, useRef } from 'react'
import { uploadDocument, reprocessDocument, getDuplicateInfo, type DuplicateDocumentInfo } from '../api/documents'

interface DocumentUploadProps {
  onUploadComplete: () => void
}

export default function DocumentUpload({ onUploadComplete }: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [reprocessing, setReprocessing] = useState(false)
  const [status, setStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null)
  const [duplicate, setDuplicate] = useState<DuplicateDocumentInfo | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setStatus(null)
    setDuplicate(null)

    try {
      const result = await uploadDocument(file)
      if (result.status === 'ready') {
        setStatus({ type: 'success', message: `${result.filename} uploaded and ready.` })
        onUploadComplete()
      } else {
        setStatus({ type: 'error', message: `${result.filename} failed to process.` })
      }
    } catch (error) {
      const dupInfo = getDuplicateInfo(error)
      if (dupInfo) {
        setDuplicate(dupInfo)
      } else {
        setStatus({ type: 'error', message: "Couldn't upload that file. Try again." })
      }
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  async function handleReprocess() {
    if (!duplicate) return
    setReprocessing(true)
    try {
      const result = await reprocessDocument(duplicate.document_id)
      setStatus({ type: 'success', message: `${result.filename} reprocessed and ready.` })
      setDuplicate(null)
      onUploadComplete()
    } catch {
      setStatus({ type: 'error', message: "Couldn't reprocess that document. Try again." })
    } finally {
      setReprocessing(false)
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

      {duplicate && (
        <div className="text-sm rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 max-w-sm">
          <p className="text-amber-800">
            "{duplicate.filename}" was already uploaded on{' '}
            {new Date(duplicate.uploaded_at).toLocaleDateString()}.
          </p>
          {duplicate.reprocess_recommended && (
            <p className="text-amber-700 mt-1">
              It was indexed with older settings — reprocessing will improve search results.
            </p>
          )}
          <div className="flex gap-2 mt-2">
            <button
              onClick={handleReprocess}
              disabled={reprocessing}
              className="text-xs rounded border border-amber-400 px-2 py-1 hover:bg-amber-100 disabled:opacity-50"
            >
              {reprocessing ? 'Reprocessing...' : 'Reprocess anyway'}
            </button>
            <button
              onClick={() => setDuplicate(null)}
              className="text-xs rounded border border-gray-300 px-2 py-1 hover:bg-gray-50"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}
    </div>
  )
}