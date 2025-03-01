import { fileURLToPath, URL } from "node:url";
import path from 'path'

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  base: "/adminonefrontend/",
  plugins: [vue()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, 'src'),
      'ant-design-vue': path.resolve(__dirname, 'node_modules/ant-design-vue'),
    },
  },
  css: {
    preprocessorOptions: {
      less: {
        javascriptEnabled: true,
      },
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    },
    historyApiFallback: {
      rewrites: [
        { from: /^\/adminonefrontend\/.*$/, to: '/adminonefrontend/index.html' }
      ]
    },
    allowedHosts: [
      'localhost',
      'hcss',
      '.local',
      '.localhost'
    ]
  }
});
