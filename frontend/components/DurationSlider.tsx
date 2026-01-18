'use client'

import { Clock } from 'lucide-react'

interface DurationSliderProps {
  value: number
  onChange: (value: number) => void
  disabled?: boolean
}

export default function DurationSlider({ value, onChange, disabled = false }: DurationSliderProps) {
  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
          <Clock className="w-4 h-4" />
          Video Duration
        </label>
        <span className="text-2xl font-bold text-primary-600">{value}s</span>
      </div>
      
      <input
        type="range"
        min="1"
        max="20"
        step="1"
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        disabled={disabled}
        className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed
          [&::-webkit-slider-thumb]:appearance-none
          [&::-webkit-slider-thumb]:w-5
          [&::-webkit-slider-thumb]:h-5
          [&::-webkit-slider-thumb]:rounded-full
          [&::-webkit-slider-thumb]:bg-primary-600
          [&::-webkit-slider-thumb]:cursor-pointer
          [&::-webkit-slider-thumb]:shadow-md
          [&::-webkit-slider-thumb]:hover:bg-primary-700
          [&::-webkit-slider-thumb]:transition-colors
          [&::-moz-range-thumb]:w-5
          [&::-moz-range-thumb]:h-5
          [&::-moz-range-thumb]:rounded-full
          [&::-moz-range-thumb]:bg-primary-600
          [&::-moz-range-thumb]:border-0
          [&::-moz-range-thumb]:cursor-pointer
          [&::-moz-range-thumb]:shadow-md
          [&::-moz-range-thumb]:hover:bg-primary-700
          [&::-moz-range-thumb]:transition-colors"
      />
      
      <div className="flex justify-between text-xs text-slate-500">
        <span>1s</span>
        <span>5s</span>
        <span>10s</span>
        <span>15s</span>
        <span>20s</span>
      </div>
      
      <p className="text-sm text-slate-600 bg-slate-50 rounded p-3">
        Shorter = faster drawing • Longer = more detailed animation
      </p>
    </div>
  )
}
