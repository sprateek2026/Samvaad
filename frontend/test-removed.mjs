import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:5184/', { waitUntil: 'networkidle', timeout: 30000 });
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.screenshot({ path: 'login-updated.png', fullPage: true });
    
    // Check if Access Credentials text is gone
    const hasAccessCred = await page.locator('text=Access Credentials').isVisible().catch(() => false);
    console.log(hasAccessCred ? '❌ Access Credentials still visible' : '✅ Access Credentials removed');
    
    // Verify other elements are still there
    const hasLoginAs = await page.locator('text=Login As').isVisible();
    const hasMobile = await page.locator('text=Mobile Number').isVisible();
    console.log((hasLoginAs && hasMobile) ? '✅ Login form elements intact' : '❌ Form elements missing');
    
  } finally {
    await browser.close();
  }
})();
