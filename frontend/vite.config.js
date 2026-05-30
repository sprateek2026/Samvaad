import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    // Pre-transform critical modules on dev-server start so the first browser
    // load doesn't hit blank pages while Vite lazily compiles the module graph.
    warmup: {
      clientFiles: [
        './src/main.jsx',
        './src/App.jsx',
        './src/api.js',
        './src/i18n.js',
        './src/components/Layout.jsx',
        './src/components/ErrorBoundary.jsx',
        './src/pages/Login.jsx',
        './src/pages/CitizenDashboard.jsx',
        './src/pages/CorporatorDashboard.jsx',
        './src/pages/Admin.jsx',
      ],
    },
  },
})
