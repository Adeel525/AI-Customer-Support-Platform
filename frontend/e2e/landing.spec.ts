import { test, expect } from "@playwright/test";

test("landing page loads", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("h1")).toContainText("Support that learns from");
});

test("navigation to signup", async ({ page }) => {
  await page.goto("/");
  await page.click("text=Get Started");
  await expect(page).toHaveURL(/signup/);
});

test("navigation to login", async ({ page }) => {
  await page.goto("/login");
  await expect(page.locator("text=Welcome back")).toBeVisible();
});
