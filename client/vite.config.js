import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  esbuild: {
    loader: "tsx", // TSX instead of JSX
    include: /src\/.*\.[jt]sx?$/, // still supports .js/.jsx/.ts/.tsx
  },
  optimizeDeps: {
    include: ['@emotion/styled'],
    esbuild: {
      loader: {
        '.js': 'jsx',
        '.jsx': 'jsx',
        '.ts': 'tsx',
        '.tsx': 'tsx',
      },
    },
  },
})