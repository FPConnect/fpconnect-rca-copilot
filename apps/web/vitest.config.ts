import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./jest.setup.js'],
    globals: true,
    coverage: {
      reporter: ['text', 'json', 'html'],
    },
  },
});
