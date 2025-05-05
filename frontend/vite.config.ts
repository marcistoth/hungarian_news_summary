import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import fs from 'node:fs'
import path from 'node:path'
import type { Plugin } from 'vite'

// Create a properly typed custom plugin
const copy404Plugin: Plugin = {
  name: 'copy-404-html',
  closeBundle() {
    const publicPath = path.resolve('./public/404.html')
    const distPath = path.resolve('./dist/404.html')
    
    if (fs.existsSync(publicPath)) {
      fs.copyFileSync(publicPath, distPath)
      console.log('✓ Copied 404.html to dist/')
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    copy404Plugin
  ],
  base: '/hungarian_news_summary/',
  server: {
    port: 5173
  }
})