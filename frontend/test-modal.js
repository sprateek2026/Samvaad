import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:5173/admin', { waitUntil: 'networkidle' });

  // Wait for page to load
  await page.waitForTimeout(3000);

  // Check what's on the page
  const pageContent = await page.content();
  console.log('Page loaded. Checking for modals...');

  // Look for any buttons
  const buttons = await page.locator('button').all();
  console.log(`Found ${buttons.length} total buttons`);

  // List first 10 button texts
  for (let i = 0; i < Math.min(10, buttons.length); i++) {
    const text = await buttons[i].textContent();
    console.log(`  Button ${i}: "${text.trim()}"`);
  }

  // Check if we're on login page
  const loginForm = await page.locator('input[type="email"], input[placeholder*="email"]').first();
  if (await loginForm.isVisible()) {
    console.log('\n⚠️ Page is on login screen - admin page requires authentication');
  }

  // Check if there's data in the page
  const adminTabs = await page.locator('button:has-text("Dashboard"), button:has-text("Representatives")').all();
  console.log(`Found ${adminTabs.length} admin tabs`);

  await browser.close();
})();
