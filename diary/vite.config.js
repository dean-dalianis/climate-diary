import {defineConfig} from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {port: 9000, host: true},
    mimeTypes: {
        'application/javascript': ['js'],
        'application/json': ['json'],
        'application/octet-stream': ['svg'], // Add this line to allow SVG files
        'text/css': ['css'],
        'text/html': ['html'],
        'text/plain': ['txt'],
        'text/xml': ['xml'],
    },
})
