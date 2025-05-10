import * as galata from "@jupyterlab/galata";
import * as fs from "fs";

import { expect } from "@jupyterlab/galata";
import { Page } from "@playwright/test";
import Database from "better-sqlite3";

const path = process.env.MINISPOT_DATABASE!;

const test = galata.test.extend({
  waitForApplication: async ({}, use) => {
    await use(async (page: Page) => {
      await page.waitForSelector("#main-panel");
    });
  }
});

test("type-and-run", async ({ page }) => {
  const timeout = { timeout: 10 * 1000 };

  // delete database if exists
  if (fs.existsSync(path)) fs.unlinkSync(path);

  // create new notebook
  const popup = page.waitForEvent("popup");
  await page.click('text="New"');
  await page
    .locator('[data-command="notebook:create-new"] >> text="Python (isolated)"')
    .click();

  // wait for new tab
  const notebook = await popup;
  const indicator = notebook.locator(".jp-Notebook-ExecutionIndicator");

  // wait for kernel ready
  await expect(indicator).toHaveAttribute("data-status", "idle", timeout);

  // --------------------------------------------------------------------------
  // write code
  await notebook
    .locator(".jp-Cell-inputArea >> .cm-editor >> .cm-content")
    .fill("print(1)");

  // run cell
  await notebook.keyboard.press("Shift+Enter");

  // wait for kernel ready
  await expect(indicator).toHaveAttribute("data-status", "idle", timeout);

  // wait for prompt number
  const prompt1 = notebook.locator(".jp-InputPrompt").nth(0);
  await expect(prompt1).toHaveText("[1]:");

  // wait for output
  notebook.locator(".jp-OutputArea-output >> pre");

  // --------------------------------------------------------------------------
  // write code
  await notebook
    .locator(".jp-Cell-inputArea >> .cm-editor >> .cm-content")
    .nth(1)
    .fill("x");

  // run cell
  await notebook.keyboard.press("Shift+Enter");

  // wait for kernel ready
  await expect(indicator).toHaveAttribute("data-status", "idle", timeout);

  // wait for prompt number
  const prompt2 = notebook.locator(".jp-InputPrompt").nth(1);
  await expect(prompt2).toHaveText("[2]:");

  // wait for output
  notebook.locator(".jp-OutputArea-output >> pre");

  // --------------------------------------------------------------------------
  const database = new Database(path);
  const rows = database.prepare("SELECT * FROM history").all();
  expect(rows).toHaveLength(2);
  console.log(rows);
  expect(rows[0]).toEqual({
    session: 1,
    restart: 0,
    excount: 1,
    source: "print(1)",
    trace: null
  });
  expect(rows[1]).toEqual({
    session: 1,
    restart: 0,
    excount: 2,
    source: "x",
    trace:
      "---------------------------------------------------------------------------\n" +
      "NameError                                 Traceback (most recent call last)\n" +
      "Cell In[2], line 1\n" +
      "----> 1 x\n" +
      "\n" +
      "NameError: name 'x' is not defined"
  });

  // close
  await notebook.close();
  await page.close();

  // unlock
  const lock = `${path}.lock`;
  if (fs.existsSync(lock)) fs.rmdirSync(lock);
});
