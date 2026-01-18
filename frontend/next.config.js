/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',  // Enable static export for GitHub Pages
  basePath: '/pencil-draw',  // GitHub repo name
  assetPrefix: '/pencil-draw/',
  images: {
    unoptimized: true,  // Required for static export
  },
  trailingSlash: true,
}

module.exports = nextConfig
