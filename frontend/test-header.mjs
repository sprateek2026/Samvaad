import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:5184/', { waitUntil: 'networkidle', timeout: 30000 });
    
    // Get header/nav element
    const nav = await page.locator('nav').first();
    await nav.screenshot({ path: 'navbar-header.png' });
    console.log('✅ Navbar screenshot saved');
    
    // Get login card header
    const loginCard = await page.locator('div.bg-white.rounded-xl').first();
    const cardHeader = await loginCard.locator('div:has-text("Samvaad")').first();
    await cardHeader.screenshot({ path: 'login-card-header.png' });
    console.log('✅ Login card header screenshot saved');
    
    // Get full page screenshot with viewport 1920x1080
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.screenshot({ path: 'full-page.png', fullPage: true });
    console.log('✅ Full page screenshot saved');
    
  } finally {
    await browser.close();
  }
})();
