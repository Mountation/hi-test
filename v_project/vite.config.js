import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      // proxy API requests to Django backend running on localhost:8000
      '/': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
