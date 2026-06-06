import { defineConfig } from "vite";

export default defineConfig({
  build: {
    lib: {
      entry: "src/widget.ts",
      name: "SupportAIWidget",
      fileName: "widget",
      formats: ["iife"],
    },
    outDir: "dist",
    emptyOutDir: true,
  },
});
