'use client'

import Image from 'next/image'
import { useState } from 'react'

interface HandStyleSelectorProps {
  selected: string
  onSelect: (style: string) => void
  disabled?: boolean
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const handStyles = [
  {
    id: 'hand_1',
    name: 'Hand Style 1',
    description: 'Natural writing pose',
    image: `${API_URL}/assets/hands/1.png`,
    hasImage: true
  },
  {
    id: 'hand_2',
    name: 'Hand Style 2',
    description: 'Artistic grip',
    image: `${API_URL}/assets/hands/2.png`,
    hasImage: true
  },
  {
    id: 'hand_3',
    name: 'Hand Style 3',
    description: 'Sketch pose',
    image: `${API_URL}/assets/hands/3.png`,
    hasImage: true
  },
  {
    id: 'hand_4',
    name: 'Hand Style 4',
    description: 'Drawing grip',
    image: `${API_URL}/assets/hands/4.png`,
    hasImage: true
  },
  {
    id: 'generated',
    name: 'Simple Hand',
    description: 'Basic generated hand',
    image: '',
    hasImage: false
  }
]

export default function HandStyleSelector({ selected, onSelect, disabled = false }: HandStyleSelectorProps) {
  const [imageErrors, setImageErrors] = useState<Record<string, boolean>>({})

  const handleImageError = (styleId: string) => {
    setImageErrors(prev => ({ ...prev, [styleId]: true }))
  }

  return (
    <div className="w-full">
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {handStyles.map((style) => (
          <button
            key={style.id}
            onClick={() => onSelect(style.id)}
            disabled={disabled}
            className={`p-3 rounded-lg border-2 text-center transition-all ${
              selected === style.id
                ? 'border-primary-600 bg-primary-50 shadow-md ring-2 ring-primary-200'
                : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            <div className="flex flex-col items-center gap-2">
              {/* Hand Image Preview */}
              <div className="w-16 h-20 relative bg-slate-100 rounded overflow-hidden flex items-center justify-center">
                {style.hasImage && !imageErrors[style.id] ? (
                  <img
                    src={style.image}
                    alt={style.name}
                    className="w-full h-full object-contain"
                    onError={() => handleImageError(style.id)}
                  />
                ) : (
                  <span className="text-3xl">✏️</span>
                )}
              </div>
              
              {/* Name */}
              <div className="text-center">
                <h3 className="font-medium text-sm text-slate-900">{style.name}</h3>
                <p className="text-xs text-slate-500">{style.description}</p>
              </div>
              
              {/* Selection indicator */}
              {selected === style.id && (
                <div className="w-5 h-5 rounded-full bg-primary-600 flex items-center justify-center">
                  <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
