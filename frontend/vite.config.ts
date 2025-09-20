import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,          // listen on 0.0.0.0
    port: 5173,
    strictPort: true,
    hmr: { clientPort: 5173 },
    watch: {
      usePolling: true,  // 👈 important for Docker on Windows
      interval: 200,
    },
  }
})
