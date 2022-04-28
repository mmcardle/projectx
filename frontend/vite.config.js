import { defineConfig, splitVendorChunkPlugin } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), splitVendorChunkPlugin()],
  server: {
    proxy: {
      // with options
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        xfwd: false,
      },
      '/app': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        xfwd: false,
      },
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true
      }
    }
  }
})
