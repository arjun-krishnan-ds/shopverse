import { defineConfig } from 'vite'
import path from 'path'

export default defineConfig(({ command }) => ({

  /*
  |--------------------------------------------------------------------------
  | Base URL
  |--------------------------------------------------------------------------
  |
  | Development:
  |   Assets served directly from Vite dev server
  |
  | Production:
  |   Django serves built assets from /static/dist/
  |
  */

  base: command === 'build'
    ? '/static/dist/'
    : 'http://127.0.0.1:5173/',

  /*
  |--------------------------------------------------------------------------
  | Build Configuration
  |--------------------------------------------------------------------------
  */

  build: {

    // Build output → project_root/static/dist/
    outDir: '../static/dist',

    emptyOutDir: true,

    manifest: true,

    sourcemap: false,

    minify: 'esbuild',

    reportCompressedSize: true,

    rollupOptions: {
      input: path.resolve(__dirname, 'src/main.js'),

      output: {

        entryFileNames: 'js/[name]-[hash].js',

        chunkFileNames: 'js/chunks/[name]-[hash].js',

        assetFileNames: ({ name = '' }) => {

          if (/\.(gif|jpe?g|png|svg|webp|ico)$/i.test(name)) {
            return 'images/[name]-[hash][extname]'
          }

          if (/\.css$/i.test(name)) {
            return 'css/[name]-[hash][extname]'
          }

          return 'assets/[name]-[hash][extname]'
        },

        manualChunks: {
          alpine: ['alpinejs'],
          axios: ['axios'],
        },
      },
    },
  },

  /*
  |--------------------------------------------------------------------------
  | Dev Server
  |--------------------------------------------------------------------------
  */

  server: {

    host: '127.0.0.1',

    port: 5173,

    strictPort: true,

    open: false,

    cors: true,

    hmr: {
      host: '127.0.0.1',
      protocol: 'ws',
    },

    proxy: {

      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/cart': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/products': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/orders': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/accounts': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/wishlist': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/reviews': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/coupons': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/delivery': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/payments': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/analytics': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/static': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },

  /*
  |--------------------------------------------------------------------------
  | Path Aliases
  |--------------------------------------------------------------------------
  */

  resolve: {

    alias: {

      '@': path.resolve(__dirname, './src'),

      '@api': path.resolve(__dirname, './src/api'),

      '@components': path.resolve(__dirname, './src/components'),

      '@stores': path.resolve(__dirname, './src/stores'),

      '@pages': path.resolve(__dirname, './src/pages'),

      '@utils': path.resolve(__dirname, './src/utils'),

      '@styles': path.resolve(__dirname, './src/styles'),
    },
  },

  /*
  |--------------------------------------------------------------------------
  | Global Defines
  |--------------------------------------------------------------------------
  */

  define: {
    __DEV__: JSON.stringify(command !== 'build'),
  },
}))