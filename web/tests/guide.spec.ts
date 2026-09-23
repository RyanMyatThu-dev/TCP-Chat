import { test, expect } from "@playwright/test";

test("installation and join path work without sending invitation codes", async ({
  page,
  context,
}) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  await page.getByRole("button", { name: "Windows", exact: true }).click();
  await expect(
    page.getByText("powershell -ExecutionPolicy", { exact: false }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Copy Neon Chat installation command" })
    .click();
  expect(await page.evaluate(() => navigator.clipboard.readText())).toContain(
    "uv tool install",
  );
  await page.getByRole("button", { name: /Join a friend/ }).click();
  await page.getByLabel("Your friend’s room code").fill("bad");
  await expect(page.getByLabel("Your friend’s room code")).toHaveAttribute(
    "aria-invalid",
    "true",
  );
  await expect(
    page.getByRole("button", { name: "Copy your join command" }),
  ).toHaveCount(0);
  const requests: string[] = [];
  page.on("request", (request) => requests.push(request.url()));
  await page.getByLabel("Your friend’s room code").fill("abcd1234efgh");
  await page.getByRole("button", { name: "Copy your join command" }).click();
  expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(
    "neon-chat join ABCD-1234-EFGH",
  );
  expect(requests.some((url) => /abcd|1234/i.test(url))).toBe(false);
  expect(errors).toEqual([]);
});

test("responsive layout and reduced motion", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await expect(page.locator(".cursor-ring")).toBeHidden();
  await page.screenshot({ path: "/tmp/neon-guide-mobile.png", fullPage: true });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.screenshot({
    path: "/tmp/neon-guide-desktop.png",
    fullPage: true,
  });
  const backgrounds = await page
    .locator("*")
    .evaluateAll((nodes) =>
      nodes.map((node) => getComputedStyle(node).backgroundImage),
    );
  expect(backgrounds.some((value) => value.includes("gradient"))).toBe(false);
});

test("cursor eases toward movement, click pixels expire, and favicon loads", async ({
  page,
}) => {
  await page.goto("/");
  await page.mouse.move(100, 100);
  await expect(page.locator(".cursor-ring")).toHaveCSS("opacity", "1");
  await page.mouse.move(500, 250);
  await expect
    .poll(async () => {
      const box = await page.locator(".cursor-ring").boundingBox();
      return Math.abs((box?.x ?? 0) - 486);
    })
    .toBeLessThan(1);
  await page.mouse.click(500, 250);
  await expect(page.locator(".pixel-burst i")).toHaveCount(8);
  await expect(page.locator(".pixel-burst")).toHaveCount(0);
  const favicon = await page.locator('link[rel="icon"]').getAttribute("href");
  const response = await page.request.get(favicon!);
  expect(response.ok()).toBe(true);
  expect(await response.text()).toContain("<svg");
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.mouse.click(500, 250);
  await expect(page.locator(".cursor-effects")).toBeHidden();
  await expect(page.locator(".pixel-burst")).toHaveCount(0);
});
