import { defineConfig } from "@playwright/test";

process.env.MINISPOT_DATABASE = ".minispot.db";

export default defineConfig({
  use: {
    appPath: ""
  },
  webServer: [
    {
      command: "minispot --playwright",
      stdout: "pipe",
      stderr: "pipe",
      env: {
        JUPYTER_CONFIG_PATH: "jupyter"
      }
    }
  ]
});
