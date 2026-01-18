/**
 * API client for backend communication.
 */

// For GitHub Pages, the backend runs locally on user's machine
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8123'

export type DrawingDirection = 
  | 'left_to_right'
  | 'right_to_left'
  | 'top_to_bottom'
  | 'bottom_to_top'
  | 'center_out'
  | 'element_by_element'

export type ElementDirection = 'default' | 'row_wise' | 'column_wise'

export type DrawingMode = 'normal' | 'outline_only' | 'outline_then_fill'

export interface GenerateVideoRequest {
  image: string
  duration: number
  hand_style: string
  drawing_direction: DrawingDirection
  element_direction: ElementDirection
  drawing_mode: DrawingMode
  output_format: 'mp4' | 'gif'
}

export interface GenerateVideoResponse {
  status: 'success'
  video_url: string
  file_id: string
  duration_actual: number
  frames_generated: number
  file_size_mb?: number
}

export interface ErrorResponse {
  status: 'error'
  message: string
  code: string
}

/**
 * Generate sketch animation video.
 */
export async function generateVideo(
  request: GenerateVideoRequest
): Promise<GenerateVideoResponse> {
  const response = await fetch(`${API_URL}/api/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.message || 'Failed to generate video')
  }

  return data
}

/**
 * Check API health.
 */
export async function checkHealth(): Promise<any> {
  const response = await fetch(`${API_URL}/api/health`)
  return response.json()
}
