import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [vue(), vueDevTools()],

  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },

  server: {
    port: 3000,
    open: true,
  },

  build: {
    outDir: 'dist',
    chunkSizeWarningLimit: 700,   // Naive UI + ECharts 라 기본 500KB 로는 경고가 뜬다
    rollupOptions: {
      output: {
        /* 모든 의존성이 하나로 묶이면 우리 코드 한 줄만 고쳐도
         * 사용자는 1MB 전체를 다시 받는다. 라이브러리는 자주 안 바뀌므로
         * 따로 떼어내면 브라우저 캐시를 계속 재사용할 수 있다. */
        manualChunks: {
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-ui': ['naive-ui'],
          'vendor-chart': ['echarts', 'vue-echarts'],
        },
      },
    },
  },
})
/*
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
*/