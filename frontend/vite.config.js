import { defineConfig } from 'vite'
import react from '@vitejs/react-plugin'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // Points straight to your local FastAPI instance
        changeOrigin: true,
        secure: false,
      }
    }
  }
})