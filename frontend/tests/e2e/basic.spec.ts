import { test, expect } from "@playwright/test";

test("hero szekció betöltése és CTA interakció", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("header")).toBeVisible();
  await expect(
    page.getByRole("heading", { level: 1 }).first()
  ).toBeVisible();

  const primaryCta = page.getByRole("link", { name: /indítás/i }).first();
  await expect(primaryCta).toBeVisible();
  await primaryCta.hover();
});

test("űrlap mezők és beküldés kezelése", async ({ page }) => {
  await page.goto("/");
  const textarea = page.getByRole("textbox");
  await textarea.fill("Írj összefoglalót a Brunella architektúráról");
  const submit = page.getByRole("button", { name: /indítás/i });
  await expect(submit).toBeEnabled();
  await submit.focus();
});
