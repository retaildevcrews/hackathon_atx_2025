import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/decision-kits': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/criteria': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/rubrics': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          react: ['react', 'react-dom', 'react-router-dom'],
          mui: ['@mui/material', '@mui/icons-material'],
          vendor: ['axios']
        }
      }
    }
  }
});
