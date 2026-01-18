'use client'

import { Sparkles, Loader2 } from 'lucide-react'

interface GenerateButtonProps {
  onClick: () => void
  disabled: boolean
  isGenerating: boolean
}

export default function GenerateButton({ onClick, disabled, isGenerating }: GenerateButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`w-full py-4 px-6 rounded-lg font-bold text-lg transition-all shadow-lg ${
        disabled
          ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
          : 'bg-gradient-to-r from-primary-600 to-primary-700 text-white hover:from-primary-700 hover:to-primary-800 hover:shadow-xl'
      }`}
    >
      <span className="flex items-center justify-center gap-3">
        {isGenerating ? (
          <>
            <Loader2 className="w-6 h-6 animate-spin" />
            Generating Animation...
          </>
        ) : (
          <>
            <Sparkles className="w-6 h-6" />
            Generate Sketch Animation
          </>
        )}
      </span>
    </button>
  )
}
