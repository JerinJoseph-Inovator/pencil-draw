'use client'

import { Download, RefreshCw, Loader2, Image as ImageIcon } from 'lucide-react'

interface PreviewAreaProps {
  imageUrl: string | null
  videoUrl: string | null
  isGenerating: boolean
  onReset: () => void
}

export default function PreviewArea({ imageUrl, videoUrl, isGenerating, onReset }: PreviewAreaProps) {
  const handleDownload = async () => {
    if (!videoUrl) return

    try {
      const response = await fetch(videoUrl)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `pencil-draw-${Date.now()}.${videoUrl.endsWith('.gif') ? 'gif' : 'mp4'}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      alert('Failed to download video')
    }
  }

  return (
    <div className="w-full">
      {/* Preview Container */}
      <div className="relative aspect-video bg-slate-100 rounded-lg border border-slate-200 overflow-hidden flex items-center justify-center">
        {isGenerating && (
          <div className="absolute inset-0 bg-white bg-opacity-90 flex flex-col items-center justify-center gap-4 z-10">
            <Loader2 className="w-12 h-12 text-primary-600 animate-spin" />
            <div className="text-center">
              <p className="text-lg font-semibold text-slate-900">Generating Animation...</p>
              <p className="text-sm text-slate-600 mt-1">This may take 10-30 seconds</p>
            </div>
          </div>
        )}

        {videoUrl && !isGenerating ? (
          <video
            src={videoUrl}
            controls
            autoPlay
            loop
            className="w-full h-full object-contain"
          />
        ) : imageUrl && !isGenerating ? (
          <img
            src={imageUrl}
            alt="Preview"
            className="w-full h-full object-contain"
          />
        ) : !isGenerating ? (
          <div className="text-center p-8">
            <div className="w-20 h-20 bg-slate-200 rounded-full flex items-center justify-center mx-auto mb-4">
              <ImageIcon className="w-10 h-10 text-slate-400" />
            </div>
            <p className="text-slate-600 font-medium">Upload an image to get started</p>
            <p className="text-sm text-slate-500 mt-2">Your preview will appear here</p>
          </div>
        ) : null}
      </div>

      {/* Action Buttons */}
      {videoUrl && !isGenerating && (
        <div className="mt-4 flex gap-3">
          <button
            onClick={handleDownload}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors shadow-md"
          >
            <Download className="w-5 h-5" />
            Download Video
          </button>
          <button
            onClick={onReset}
            className="px-6 py-3 bg-slate-200 text-slate-700 rounded-lg font-semibold hover:bg-slate-300 transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* Info Cards */}
      {!videoUrl && !isGenerating && (
        <div className="mt-6 space-y-3">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 text-sm mb-1">💡 Pro Tip</h4>
            <p className="text-blue-800 text-sm">
              Use high-contrast images for best results. Clear outlines produce the most realistic animations.
            </p>
          </div>
          
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <h4 className="font-semibold text-amber-900 text-sm mb-1">⚡ Fast Processing</h4>
            <p className="text-amber-800 text-sm">
              Most videos generate in under 15 seconds. Complex images may take longer.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
