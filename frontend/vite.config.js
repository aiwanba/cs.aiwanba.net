import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5010',
        changeOrigin: true
      },
      '/socket.io': {
        target: 'http://localhost:5010',
        ws: true,
        changeOrigin: true
      }
    }
  }
}) 