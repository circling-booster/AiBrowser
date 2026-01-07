import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './', // Electron에서 상대 경로로 로드하기 위해 필수
  server: {
    port: 3000,
  },
  build: {
    outDir: 'dist',
  }
});