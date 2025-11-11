import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  build: {
    // Enable cache-busting with hashed filenames
    rollupOptions: {
      output: {
        // Generate unique filenames based on content hash
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  },
  server: {
    // Prevent caching during development
    headers: {
      'Cache-Control': 'no-store',
      'Pragma': 'no-cache',
    }
  }
});
