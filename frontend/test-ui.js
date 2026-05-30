const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:5184/', { waitUntil: 'networkidle' });
    await page.screenshot({ path: 'login-page.png' });
    console.log('✅ Screenshot saved: login-page.png');
    
    // Check for megaphone icon
    const hasIcon = await page.locator('text=/📢.*Samvaad/').isVisible();
    console.log(hasIcon ? '✅ Megaphone icon visible' : '❌ Icon not found');
    
    // Check for Government of Maharashtra
    const hasGovText = await page.locator('text=Government of Maharashtra').isVisible();
    console.log(hasGovText ? '✅ Government of Maharashtra visible' : '❌ Government text not found');
    
    // Check for centered layout
    const header = await page.locator('div:has-text("Government of Maharashtra")').boundingBox();
    console.log(header ? '✅ Header layout found' : '❌ Header not found');
    
  } finally {
    await browser.close();
  }
})();
