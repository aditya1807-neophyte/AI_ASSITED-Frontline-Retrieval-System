import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// @ts-ignore
import { fileURLToPath } from 'url';
// @ts-ignore
import { dirname, resolve } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

// @ts-ignore
const path = {
  resolve: resolve,
};

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    host: 'localhost',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
