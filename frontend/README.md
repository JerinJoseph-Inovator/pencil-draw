# Pencil Draw Frontend

Next.js 14 frontend with Tailwind CSS for generating hand-drawn sketch animations.

## Quick Start

### Install Dependencies

```bash
npm install
```

### Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
npm run build
npm start
```

## Features

- **Image Upload**: Drag & drop or file picker with validation
- **Duration Control**: Slider for 1-20 second videos
- **Hand Style Selection**: Multiple skin tones and drawing tools
- **Real-time Preview**: See uploaded image and generated video
- **Download**: One-click MP4/GIF download

## Components

### ImageUploader
Handles image upload with drag & drop support using react-dropzone.

### DurationSlider
Range slider for video duration selection.

### HandStyleSelector
Grid of hand style options with visual previews.

### PreviewArea
Shows uploaded image or generated video with download capability.

### GenerateButton
Primary CTA button with loading state.

## API Integration

All backend calls are handled through `lib/api-client.ts`:

```typescript
import { generateVideo } from '@/lib/api-client'

const result = await generateVideo({
  image: base64String,
  duration: 10,
  hand_style: 'light_pencil',
  output_format: 'mp4'
})
```

## Deployment

### Vercel (Recommended)

```bash
vercel
```

### Docker

```bash
docker build -t pencil-draw-frontend .
docker run -p 3000:3000 pencil-draw-frontend
```

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **UI Components**: Custom React components
- **Icons**: Lucide React
- **File Upload**: react-dropzone
- **HTTP Client**: Fetch API

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
