export default {
  ci: {
    collect: {
      url: ["http://127.0.0.1:4173/"],
      startServerCommand: "npm run preview -- --host 127.0.0.1 --port 4173",
      numberOfRuns: 1,
      headless: true,
      settings: {
        formFactor: "desktop",
        screenEmulation: { mobile: false, width: 1366, height: 768 },
      },
    },
    assert: {
      assertions: {
        "categories:performance": ["warn", { minScore: 0.75 }],
        "categories:accessibility": ["error", { minScore: 0.9 }],
        "categories:best-practices": ["warn", { minScore: 0.85 }],
        "categories:seo": ["warn", { minScore: 0.85 }],
      },
    },
    upload: {
      target: "filesystem",
      outputDir: "./.lighthouse",
    },
  },
};
