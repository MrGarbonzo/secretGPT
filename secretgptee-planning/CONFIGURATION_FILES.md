# Configuration Files for SecretGPTee.com

## 1. Environment Variables

### `.env.example`
```bash
# API Endpoints
VUE_APP_SECRET_MCP_URL=http://localhost:3002
VUE_APP_SECRET_AI_URL=http://localhost:3003
VUE_APP_ATTESTAI_URL=http://localhost:3000

# Secret Network Configuration
VUE_APP_CHAIN_ID=secret-4
VUE_APP_CHAIN_NAME=Secret Network
VUE_APP_RPC_URL=https://lcd.spartanapi.dev
VUE_APP_REST_URL=https://lcd.spartanapi.dev

# Application Settings
VUE_APP_ENV=development
VUE_APP_VERSION=1.0.0
VUE_APP_DEBUG=true

# Security Settings
VUE_APP_MESSAGE_SIGNING_ENABLED=true
VUE_APP_REQUEST_TIMEOUT=10000
VUE_APP_MAX_RETRY_ATTEMPTS=3

# Feature Flags
VUE_APP_ENABLE_CHAT_HISTORY=true
VUE_APP_ENABLE_WALLET_CONNECT=true
VUE_APP_ENABLE_ATTESTATIONS=true
VUE_APP_ENABLE_BALANCE_REFRESH=true
```

### `.env.development`
```bash
VUE_APP_SECRET_MCP_URL=http://localhost:3002
VUE_APP_SECRET_AI_URL=http://localhost:3003
VUE_APP_ATTESTAI_URL=http://localhost:3000
VUE_APP_CHAIN_ID=pulsar-3
VUE_APP_RPC_URL=https://api.pulsar3.scrttestnet.com
VUE_APP_REST_URL=https://api.pulsar3.scrttestnet.com
VUE_APP_ENV=development
VUE_APP_DEBUG=true
```

### `.env.production`
```bash
VUE_APP_SECRET_MCP_URL=https://secret-mcp-vm.your-domain.com
VUE_APP_SECRET_AI_URL=https://secret-ai.your-domain.com
VUE_APP_ATTESTAI_URL=https://attestai.io
VUE_APP_CHAIN_ID=secret-4
VUE_APP_RPC_URL=https://lcd.spartanapi.dev
VUE_APP_REST_URL=https://lcd.spartanapi.dev
VUE_APP_ENV=production
VUE_APP_DEBUG=false
```

## 2. Package.json Dependencies

### `package.json`
```json
{
  "name": "secretgptee",
  "version": "1.0.0",
  "description": "Secret Network tech demo with ChatGPT-like interface",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .vue,.js,.jsx,.ts,.tsx",
    "format": "prettier --write .",
    "type-check": "vue-tsc --noEmit"
  },
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "^4.2.4",
    "pinia": "^2.1.6",
    "axios": "^1.5.0",
    "@keplr-wallet/cosmos": "^0.12.29",
    "@keplr-wallet/types": "^0.12.29",
    "@tailwindcss/forms": "^0.5.4",
    "@tailwindcss/typography": "^0.5.9",
    "@headlessui/vue": "^1.7.14",
    "@heroicons/vue": "^2.0.18",
    "date-fns": "^2.30.0",
    "crypto-js": "^4.1.1",
    "marked": "^7.0.4",
    "highlight.js": "^11.8.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.3.1",
    "vite": "^4.4.9",
    "tailwindcss": "^3.3.3",
    "autoprefixer": "^10.4.15",
    "postcss": "^8.4.28",
    "eslint": "^8.47.0",
    "eslint-plugin-vue": "^9.17.0",
    "@vue/eslint-config-prettier": "^8.0.0",
    "prettier": "^3.0.2",
    "vue-tsc": "^1.8.8"
  }
}
```

## 3. Vite Configuration

### `vite.config.js`
```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3001,
    host: true,
    proxy: {
      '/api/mcp': {
        target: process.env.VUE_APP_SECRET_MCP_URL || 'http://localhost:3002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/mcp/, '/api')
      },
      '/api/ai': {
        target: process.env.VUE_APP_SECRET_AI_URL || 'http://localhost:3003',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/ai/, '/api')
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          wallet: ['@keplr-wallet/cosmos', '@keplr-wallet/types'],
          ui: ['@headlessui/vue', '@heroicons/vue'],
          utils: ['axios', 'crypto-js', 'date-fns']
        }
      }
    }
  },
  define: {
    __VUE_OPTIONS_API__: false,
    __VUE_PROD_DEVTOOLS__: false
  }
})
```

## 4. Tailwind Configuration

### `tailwind.config.js`
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // ChatGPT-inspired color palette
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          850: '#1a202c',
          900: '#111827',
          950: '#0d1117'
        },
        // Secret Network brand colors
        secret: {
          50: '#e6f7ff',
          100: '#bae7ff',
          200: '#7dd3fc',
          300: '#38bdf8',
          400: '#0ea5e9',
          500: '#0284c7',
          600: '#0369a1',
          700: '#075985',
          800: '#0c4a6e',
          900: '#0a3a5c'
        },
        // Status colors
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace']
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '100': '25rem',
        '112': '28rem'
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-subtle': 'bounceSubtle 2s infinite'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideIn: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' }
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-2px)' }
        }
      },
      backdropBlur: {
        xs: '2px'
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ]
}
```

## 5. PostCSS Configuration

### `postcss.config.js`
```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {}
  }
}
```

## 6. ESLint Configuration

### `.eslintrc.cjs`
```javascript
module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    es2022: true
  },
  extends: [
    'eslint:recommended',
    '@vue/eslint-config-prettier',
    'plugin:vue/vue3-recommended'
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
    'vue/multi-word-component-names': 'off',
    'vue/no-unused-vars': 'error',
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off'
  },
  globals: {
    __VUE_OPTIONS_API__: 'readonly',
    __VUE_PROD_DEVTOOLS__: 'readonly'
  }
}
```

## 7. Prettier Configuration

### `.prettierrc`
```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "none",
  "printWidth": 80,
  "endOfLine": "lf",
  "vueIndentScriptAndStyle": true
}
```

## 8. Nginx Reverse Proxy Configuration

### `nginx.conf` (for production deployment)
```nginx
server {
    listen 80;
    server_name secretgptee.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name secretgptee.com;

    ssl_certificate /path/to/ssl/secretgptee.com.crt;
    ssl_certificate_key /path/to/ssl/secretgptee.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    root /var/www/secretgptee/dist;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Handle Vue.js routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy to secret_network_mcp VM
    location /api/mcp/ {
        proxy_pass http://secret-mcp-vm:3002/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # API proxy to SecretAI
    location /api/ai/ {
        proxy_pass http://secret-ai-vm:3003/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Existing attestAI.io configuration
server {
    listen 443 ssl http2;
    server_name attestai.io;
    
    ssl_certificate /path/to/ssl/attestai.io.crt;
    ssl_certificate_key /path/to/ssl/attestai.io.key;
    
    # Existing attestAI configuration...
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 9. Docker Configuration (Optional)

### `Dockerfile`
```dockerfile
# Build stage
FROM node:18-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 10. Main CSS File

### `src/assets/css/main.css`
```css
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

/* Custom CSS Variables */
:root {
  --header-height: 60px;
  --sidebar-width: 280px;
  --message-max-width: 48rem;
  --transition-speed: 0.2s;
}

/* Global Styles */
html {
  scroll-behavior: smooth;
}

body {
  font-family: Inter, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Custom Components */
.scrollbar-thin {
  scrollbar-width: thin;
  scrollbar-color: rgb(107 114 128) transparent;
}

.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: rgb(107 114 128);
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background-color: rgb(75 85 99);
}

/* Chat Message Styles */
.message-user {
  @apply bg-blue-600 text-white;
}

.message-ai {
  @apply bg-gray-700 text-gray-100;
}

.message-system {
  @apply bg-gray-600 text-gray-300 text-sm italic;
}

/* Button Variants */
.btn-primary {
  @apply bg-secret-500 hover:bg-secret-600 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200;
}

.btn-secondary {
  @apply bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200;
}

.btn-ghost {
  @apply hover:bg-gray-700 text-gray-300 font-medium py-2 px-4 rounded-lg transition-colors duration-200;
}

/* Status Indicators */
.status-healthy {
  @apply text-green-400;
}

.status-warning {
  @apply text-yellow-400;
}

.status-error {
  @apply text-red-400;
}

.status-loading {
  @apply text-blue-400 animate-pulse;
}

/* Animation Classes */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(-100%);
}
```

This comprehensive configuration setup provides everything needed for a smooth Claude Code build process, with all the environment variables, build tools, styling, and deployment configurations ready to go.
