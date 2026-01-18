'use client'

import { useState } from 'react'
import ImageUploader from '@/components/ImageUploader'
import DurationSlider from '@/components/DurationSlider'
import HandStyleSelector from '@/components/HandStyleSelector'
import PreviewArea from '@/components/PreviewArea'
import GenerateButton from '@/components/GenerateButton'
import { generateVideo, DrawingDirection, ElementDirection, DrawingMode } from '@/lib/api-client'
import { Loader2, Sparkles, ArrowRight, ArrowLeft, ArrowDown, ArrowUp, Target, Layers, Pen, PaintBucket, Brush, Rows, Columns } from 'lucide-react'

export default function Home() {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [duration, setDuration] = useState<number>(10)
  const [handStyle, setHandStyle] = useState<string>('hand_1')
  const [outputFormat, setOutputFormat] = useState<'mp4' | 'gif'>('mp4')
  const [drawingDirection, setDrawingDirection] = useState<DrawingDirection>('left_to_right')
  const [elementDirection, setElementDirection] = useState<ElementDirection>('default')
  const [drawingMode, setDrawingMode] = useState<DrawingMode>('normal')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedVideoUrl, setGeneratedVideoUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState<string>('')

  const handleGenerate = async () => {
    if (!uploadedImage) {
      setError('Please upload an image first')
      return
    }

    setIsGenerating(true)
    setError(null)
    setGeneratedVideoUrl(null)
    setProgress('Processing image...')

    try {
      // Remove data URL prefix if present
      const base64Image = uploadedImage.includes(',') 
        ? uploadedImage.split(',')[1] 
        : uploadedImage

      const result = await generateVideo({
        image: base64Image,
        duration,
        hand_style: handStyle,
        output_format: outputFormat,
        drawing_direction: drawingDirection,
        element_direction: elementDirection,
        drawing_mode: drawingMode
      })

      setProgress('Video generated successfully!')
      
      // Construct full URL for video download
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      setGeneratedVideoUrl(`${apiUrl}${result.video_url}`)
      
    } catch (err: any) {
      setError(err.message || 'Failed to generate video')
      setProgress('')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleReset = () => {
    setUploadedImage(null)
    setGeneratedVideoUrl(null)
    setError(null)
    setProgress('')
    setDuration(10)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-primary-600" />
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Pencil Draw</h1>
              <p className="text-slate-600 text-sm">Transform images into hand-drawn animations</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Controls */}
          <div className="space-y-6">
            {/* Image Upload */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">1. Upload Image</h2>
              <ImageUploader 
                onImageUpload={setUploadedImage}
                currentImage={uploadedImage}
              />
            </div>

            {/* Duration Slider */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">2. Set Duration</h2>
              <DurationSlider 
                value={duration}
                onChange={setDuration}
                disabled={isGenerating}
              />
            </div>

            {/* Hand Style Selector */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">3. Choose Hand Style</h2>
              <HandStyleSelector 
                selected={handStyle}
                onSelect={setHandStyle}
                disabled={isGenerating}
              />
            </div>

            {/* Drawing Direction */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">4. Drawing Direction</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {[
                  { value: 'left_to_right', label: 'Left → Right', icon: ArrowRight },
                  { value: 'right_to_left', label: 'Right → Left', icon: ArrowLeft },
                  { value: 'top_to_bottom', label: 'Top → Bottom', icon: ArrowDown },
                  { value: 'bottom_to_top', label: 'Bottom → Top', icon: ArrowUp },
                  { value: 'center_out', label: 'Center Out', icon: Target },
                  { value: 'element_by_element', label: 'By Element', icon: Layers },
                ].map(({ value, label, icon: Icon }) => (
                  <button
                    key={value}
                    onClick={() => setDrawingDirection(value as DrawingDirection)}
                    disabled={isGenerating}
                    className={`flex flex-col items-center gap-2 p-3 rounded-lg border-2 transition-all ${
                      drawingDirection === value
                        ? 'border-primary-600 bg-primary-50 text-primary-700'
                        : 'border-slate-200 hover:border-slate-300 text-slate-600'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-xs font-medium">{label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Element Direction (only shown when element_by_element is selected) */}
            {drawingDirection === 'element_by_element' && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h2 className="text-xl font-semibold text-slate-900 mb-4">5. Element Organization</h2>
                <p className="text-sm text-slate-500 mb-4">
                  Choose how to organize detected elements. Elements are assigned based on where they START.
                </p>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    onClick={() => setElementDirection('default')}
                    disabled={isGenerating}
                    className={`flex flex-col items-center gap-3 p-4 rounded-lg border-2 transition-all ${
                      elementDirection === 'default'
                        ? 'border-primary-600 bg-primary-50 text-primary-700'
                        : 'border-slate-200 hover:border-slate-300 text-slate-600'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    <Layers className="w-8 h-8" />
                    <div className="text-center">
                      <span className="text-sm font-semibold block">Default</span>
                      <span className="text-xs opacity-75">Top → Bottom half</span>
                    </div>
                    <div className="flex flex-col gap-1 mt-1">
                      <div className="w-12 h-3 bg-current opacity-40 rounded" />
                      <div className="w-12 h-3 bg-current opacity-20 rounded" />
                    </div>
                  </button>
                  <button
                    onClick={() => setElementDirection('row_wise')}
                    disabled={isGenerating}
                    className={`flex flex-col items-center gap-3 p-4 rounded-lg border-2 transition-all ${
                      elementDirection === 'row_wise'
                        ? 'border-primary-600 bg-primary-50 text-primary-700'
                        : 'border-slate-200 hover:border-slate-300 text-slate-600'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    <Rows className="w-8 h-8" />
                    <div className="text-center">
                      <span className="text-sm font-semibold block">Row-wise</span>
                      <span className="text-xs opacity-75">5 horizontal rows</span>
                    </div>
                    <div className="flex gap-1 mt-1">
                      {[1,2,3,4,5].map(i => (
                        <div key={i} className="w-8 h-2 bg-current opacity-30 rounded" />
                      ))}
                    </div>
                  </button>
                  <button
                    onClick={() => setElementDirection('column_wise')}
                    disabled={isGenerating}
                    className={`flex flex-col items-center gap-3 p-4 rounded-lg border-2 transition-all ${
                      elementDirection === 'column_wise'
                        ? 'border-primary-600 bg-primary-50 text-primary-700'
                        : 'border-slate-200 hover:border-slate-300 text-slate-600'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    <Columns className="w-8 h-8" />
                    <div className="text-center">
                      <span className="text-sm font-semibold block">Column-wise</span>
                      <span className="text-xs opacity-75">5 vertical columns</span>
                    </div>
                    <div className="flex gap-1 mt-1">
                      {[1,2,3,4,5].map(i => (
                        <div key={i} className="w-2 h-8 bg-current opacity-30 rounded" />
                      ))}
                    </div>
                  </button>
                </div>
              </div>
            )}

            {/* Drawing Mode */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">
                {drawingDirection === 'element_by_element' ? '6' : '5'}. Drawing Mode
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { value: 'normal', label: 'Normal', desc: 'Full color drawing', icon: Brush },
                  { value: 'outline_only', label: 'Outline Only', desc: 'Sketch effect', icon: Pen },
                  { value: 'outline_then_fill', label: 'Outline + Fill', desc: 'Draw border then color', icon: PaintBucket },
                ].map(({ value, label, desc, icon: Icon }) => (
                  <button
                    key={value}
                    onClick={() => setDrawingMode(value as DrawingMode)}
                    disabled={isGenerating}
                    className={`flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all ${
                      drawingMode === value
                        ? 'border-primary-600 bg-primary-50 text-primary-700'
                        : 'border-slate-200 hover:border-slate-300 text-slate-600'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    <Icon className="w-6 h-6" />
                    <span className="text-sm font-semibold">{label}</span>
                    <span className="text-xs opacity-75">{desc}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Output Format */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">
                {drawingDirection === 'element_by_element' ? '7' : '6'}. Output Format
              </h2>
              <div className="flex gap-4">
                <button
                  onClick={() => setOutputFormat('mp4')}
                  disabled={isGenerating}
                  className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
                    outputFormat === 'mp4'
                      ? 'bg-primary-600 text-white shadow-md'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  MP4 (Best Quality)
                </button>
                <button
                  onClick={() => setOutputFormat('gif')}
                  disabled={isGenerating}
                  className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
                    outputFormat === 'gif'
                      ? 'bg-primary-600 text-white shadow-md'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  GIF (Smaller)
                </button>
              </div>
            </div>

            {/* Generate Button */}
            <GenerateButton 
              onClick={handleGenerate}
              disabled={!uploadedImage || isGenerating}
              isGenerating={isGenerating}
            />

            {/* Progress/Error Messages */}
            {progress && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-blue-800 text-sm font-medium">{progress}</p>
              </div>
            )}
            
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 text-sm font-medium">{error}</p>
              </div>
            )}
          </div>

          {/* Right Column - Preview */}
          <div className="lg:sticky lg:top-8 h-fit">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">Preview</h2>
              <PreviewArea 
                imageUrl={uploadedImage}
                videoUrl={generatedVideoUrl}
                isGenerating={isGenerating}
                onReset={handleReset}
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-slate-600 text-sm">
          <p>Built with ❤️ for creators • Max 10MB images • 1-20 second videos</p>
        </div>
      </div>
    </main>
  )
}
