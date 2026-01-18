'use client'

import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Image as ImageIcon, X } from 'lucide-react'

interface ImageUploaderProps {
  onImageUpload: (imageData: string) => void
  currentImage: string | null
}

export default function ImageUploader({ onImageUpload, currentImage }: ImageUploaderProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024
    if (file.size > maxSize) {
      alert('File too large. Maximum size is 10MB.')
      return
    }

    // Read file as base64
    const reader = new FileReader()
    reader.onload = () => {
      const base64 = reader.result as string
      onImageUpload(base64)
    }
    reader.readAsDataURL(file)
  }, [onImageUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/webp': ['.webp']
    },
    maxFiles: 1,
    multiple: false
  })

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation()
    onImageUpload('')
  }

  return (
    <div className="w-full">
      {!currentImage ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-slate-300 hover:border-slate-400 bg-slate-50'
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center gap-3">
            <div className="p-4 bg-white rounded-full shadow-sm">
              <Upload className="w-8 h-8 text-slate-600" />
            </div>
            {isDragActive ? (
              <p className="text-slate-700 font-medium">Drop image here...</p>
            ) : (
              <>
                <p className="text-slate-700 font-medium">
                  Drag & drop an image here, or click to select
                </p>
                <p className="text-sm text-slate-500">
                  JPEG, PNG, or WebP • Max 10MB • Up to 4K resolution
                </p>
              </>
            )}
          </div>
        </div>
      ) : (
        <div className="relative group">
          <img
            src={currentImage}
            alt="Uploaded preview"
            className="w-full h-auto rounded-lg border border-slate-200 shadow-sm"
          />
          <button
            onClick={handleRemove}
            className="absolute top-3 right-3 p-2 bg-red-500 text-white rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
            title="Remove image"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  )
}
