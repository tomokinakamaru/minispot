import { FlatCompat } from "@eslint/eslintrc";
import js from "@eslint/js";
import typescriptEslint from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all
});

export default [
  {
    ignores: [".venv", "build", "labextension", "*.mjs"]
  },
  ...compat.extends(
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/eslint-recommended",
    "plugin:prettier/recommended"
  ),
  {
    plugins: {
      "@typescript-eslint": typescriptEslint
    },
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 5,
      sourceType: "module",
      parserOptions: {
        project: "tsconfig.eslint.json"
      }
    },
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
      "no-empty-pattern": "off"
    }
  }
];
