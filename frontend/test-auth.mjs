import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log('Testing Login Page (Not Logged In)...');
    await page.goto('http://localhost:5184/', { waitUntil: 'networkidle', timeout: 30000 });
    
    // Screenshot of login page
    await page.screenshot({ path: 'login-page-full.png', fullPage: true });
    console.log('✅ Login page screenshot saved');
    
    // Check navbar when NOT logged in
    const navbar = await page.locator('nav').boundingBox();
    if (navbar) {
      console.log('✅ Navigation bar visible on login page');
      
      // Check that login link is NOT visible (since not logged in)
      const hasLoginLink = await page.locator('a:has-text("Login")').isVisible().catch(() => false);
      console.log(hasLoginLink ? '⚠️ Login link visible on login page (unexpected)' : '✅ Login link hidden when not logged in');
      
      // Check that dashboard link is hidden
      const hasDashboard = await page.locator('a:has-text("Dashboard")').isVisible().catch(() => false);
      console.log(!hasDashboard ? '✅ Dashboard link hidden when not logged in' : '❌ Dashboard visible');
    }
    
    // Check for megaphone icon
    const megaphone = await page.locator('text=📢').count();
    console.log(megaphone > 0 ? `✅ Megaphone icon found (${megaphone} occurrences)` : '❌ Megaphone icon not found');
    
    // Check for Government of Maharashtra
    const govText = await page.locator('text=Government of Maharashtra').isVisible();
    console.log(govText ? '✅ Government of Maharashtra text visible' : '❌ Government text not visible');
    
    // Check for centered layout in login card
    const loginCard = await page.locator('div.bg-white.rounded-xl').first();
    const cardText = await loginCard.textContent();
    console.log(cardText.includes('Samvaad') ? '✅ Samvaad in login card' : '❌ Samvaad not in login card');
    
  } catch (e) {
    console.error('Error:', e.message);
  } finally {
    await browser.close();
  }
})();
