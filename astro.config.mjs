import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://your-name.vercel.app',
  markdown: {
    shikiConfig: {
      theme: 'dracula'
    }
  }
});
