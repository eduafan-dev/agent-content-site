import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://majestic-chimera-5b8f8b.netlify.app',
  output: 'static',
  integrations: [],
  vite: {
    ssr: {
      external: ['svgo']
    }
  }
});
